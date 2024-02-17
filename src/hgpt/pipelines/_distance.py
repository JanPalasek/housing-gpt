import contextlib

from dateutil.parser import parse

with contextlib.suppress(ImportError):
    import googlemaps


class DistancePipeline:
    def __init__(self, gmaps_api_key: str, travel_config: list):
        self.client = googlemaps.Client(key=gmaps_api_key)
        self.travel_config = travel_config

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            gmaps_api_key=crawler.settings.get("GMAPS_API_KEY"), travel_config=crawler.settings.get("TRAVEL_CONFIG", [])
        )

    def process_item(self, item, spider):
        items = []

        from_address: str = item["location"]["address"]
        for c in self.travel_config:
            to_address = c["to_address"]
            mode = c["mode"]
            departure_dt = parse(c["departure_dt"])

            # compute duration of travel
            result = self.client.distance_matrix(from_address, to_address, mode=mode, departure_time=departure_dt)
            distance = result["rows"][0]["elements"][0].get("distance", {}).get("value", None) / 1000  # in km
            duration = result["rows"][0]["elements"][0].get("duration", {}).get("value", None) / 60  # in minutes

            # store
            items.append(
                {
                    "to_address": to_address,
                    "mode": mode,
                    "departure_dt": departure_dt,
                    "duration": duration,
                    "distance": distance,
                }
            )

        item["travel"] = items
        return item
