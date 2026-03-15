import os
import json
import requests
import time
from src.config import TMDB_API_KEY, DATA_DIR, BASE_URL, POSTER_URL

def get_movie_details(movie_id):
    # fetch movie by id
    # append: credit (team crews) and keywords
    url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits,keywords"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return None

def process_movies(pages_to_fetch=2):
    all_processed_movies = []

    # create data dir, if none
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"Start fetching movie data from TMDB: {pages_to_fetch} page")

    for page in range(1, pages_to_fetch + 1):
        print(f"Fetching page: {page}...")
        url = f"{BASE_URL}/movie/top_rated?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        response = requests.get(url)

        if not response.ok:
            print(f"Failed to fetch {page} data")
            continue

        movies = response.json().get("results", [])

        for basic_movie in movies:
            movie_id = basic_movie["id"]

            # 1. Details
            details = get_movie_details(movie_id)
            if not details:
                print(f"Can not fetch movie id: {movie_id}")
                continue

            # 2. Crews
            director = "Unknown"
            for crew_member in details.get("credits", {}).get("crew", []):
                if crew_member["job"] == "Director":
                    director = crew_member["name"]
                    break
            
            # 3. Keywords
            keywords = [kw["name"] for kw in details.get("keywords", {}).get("keywords", [])]
            genres = [g["name"] for g in details.get("genres", [])]

            # 4. JSON schema
            processed_movies = {
                "movie_id": movie_id,
                "title" : details.get("title", ""),
                "release_year" : int(details.get("release_date", "0000").split("-")[0]) if details.get("release_date") else None,
                "genres" : genres,
                "searchable_text" : {
                    "overview" : details.get("overview", ""),
                    "keywords" : keywords,
                    "tagline" : details.get("tagline", "")
                },

                "technical_details" : {
                    "director" : director
                    # will be updated in further version
                },

                "metadata_for_filtering" : {
                    "vote_averate" : details.get("vote_average", 0.0),
                    "runtime_minutes" : details.get("runtime", 0)
                },

                "display_assests" : {
                    "poster_url" : f"{POSTER_URL}/w500{details.get('poster_path', '')}"
                }
            }

            # 5. Embedding payload
            payload = f"Title: {processed_movies['title']}. " \
                        f"Genres: {', '.join(genres)}. " \
                        f"Overview: {processed_movies['searchable_text']['overview']} " \
                        f"Keywords: {', '.join(keywords)}. " \
                        f"Director: {director}."
            
            processed_movies["content_payload_for_embedding"] = payload

            all_processed_movies.append(processed_movies)

            # wait 0.1s
            time.sleep(0.1)

    # save JSON file
    output_file = os.path.join(DATA_DIR, "movies_dataset.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_processed_movies, f, indent=4, ensure_ascii=False)

    print(f"Fetching complete, Saving: {len(all_processed_movies)} movies into {output_file}")

if __name__ == "__main__":
    # test 2 page (~40 flim)
    process_movies(pages_to_fetch=2)