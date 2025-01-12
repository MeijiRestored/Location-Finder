import json

import redis
import requests
from flask import Flask, jsonify

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

if app.config["USE_REDIS"]:
  redis_client = redis.StrictRedis(
    host=app.config["REDIS_HOST"],
    port=app.config["REDIS_PORT"],
    db=app.config["REDIS_DB"],
    decode_responses=True
  )
else:
  redis_client = None


def get_flag_emoji(country_code):
  return ''.join(chr(127397 + ord(char)) for char in country_code.upper())


def get_overpass_url(lat, lon):
  base_url = "https://overpass.private.coffee/api/interpreter"
  query = f"[timeout:10][out:json];is_in({lat},{lon})->.a;way(pivot.a);out%20tags;relation(pivot.a);out%20tags;"
  return f"{base_url}?data={query}"


def process_data(data, lang):
  proc_data = {
    "country": "",
    "country_code": "",
    "country_flag": "",
    "state": "",
    "city": "",
    "suburb": "",
  }

  for i in data:
    if "tags" in i and "admin_level" in i["tags"] and "boundary" in i["tags"] and i["tags"][
      "boundary"] == "administrative":
      # admin level 9 and 10: suburb
      # in case of both, 10 takes priority
      if i["tags"]["admin_level"] == "9":
        if "name:" + lang in i["tags"]:
          proc_data["suburb"] = i["tags"]["name:" + lang]
        else:
          proc_data["suburb"] = i["tags"]["name"]

      if i["tags"]["admin_level"] == "10":
        if "name:" + lang in i["tags"]:
          proc_data["suburb"] = i["tags"]["name:" + lang]
        else:
          proc_data["suburb"] = i["tags"]["name"]

      # admin level 8: city
      elif i["tags"]["admin_level"] == "8":
        if "name:" + lang in i["tags"]:
          proc_data["city"] = i["tags"]["name:" + lang]
        else:
          proc_data["city"] = i["tags"]["name"]

      # admin level 4: state/region
      elif i["tags"]["admin_level"] == "4":
        if "name:" + lang in i["tags"]:
          proc_data["state"] = i["tags"]["name:" + lang]
        else:
          proc_data["state"] = i["tags"]["name"]

      # admin level 2: country
      elif i["tags"]["admin_level"] == "2":
        if "name:" + lang in i["tags"]:
          proc_data["country"] = i["tags"]["name:" + lang]
        else:
          proc_data["country"] = i["tags"]["name"]
        if "ISO3166-1" in i["tags"]:
          proc_data["country_code"] = i["tags"]["ISO3166-1"]

    if proc_data["country_code"] != "":
      proc_data["country_flag"] = get_flag_emoji(proc_data["country_code"])

  return proc_data


def fetch_location_data(lat, lon, lang="unspecified"):
  cache_key = f"location:{lang}:{lat}:{lon}"
  if app.config["USE_REDIS"] and redis_client:
    cached_data = redis_client.get(cache_key)
    if cached_data:
      return jsonify(json.loads(cached_data))

  overpass_url = get_overpass_url(lat, lon)
  try:
    response = requests.get(overpass_url)
    response.raise_for_status()
    data = response.json()
    proc_data = process_data(data["elements"], lang)

    if app.config["USE_REDIS"] and redis_client:
      redis_client.setex(cache_key, app.config["CACHE_EXPIRY_SECONDS"], json.dumps(proc_data))

    return jsonify(proc_data)
  except requests.exceptions.RequestException as e:
    return jsonify({"error": str(e)}), 500


@app.route('/<string:lang>/<float:lat>/<float:lon>', methods=['GET'])
def get_location_data_with_lang(lang, lat, lon):
  return fetch_location_data(lat, lon, lang)


@app.route('/<float:lat>/<float:lon>', methods=['GET'])
def get_location_data(lat, lon):
  return fetch_location_data(lat, lon)


if __name__ == '__main__':
  app.run(debug=app.config["DEBUG"])
