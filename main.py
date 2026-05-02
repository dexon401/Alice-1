import logging
import os
import waitress

from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route("/")
def index():
    return ""


@app.route("/post", methods=["POST"])
def main():
    logging.info(f"Request: {request.json!r}")

    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {"end_session": False},
    }

    handle_dialog(request.json, response)

    logging.info(f"Response:  {response!r}")

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req["session"]["user_id"]

    if req["session"]["new"]:
        sessionStorage[user_id] = {
            "suggests": [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            "elephant_bought": False,
        }
        res["response"]["text"] = "Привет! Купи слона!"
        res["response"]["buttons"] = get_suggests(user_id)
        return

    if any(
        [
            i in req["request"]["original_utterance"].lower()
            for i in ["ладно", "куплю", "покупаю", "хорошо"]
        ]
    ):
        if not sessionStorage[user_id]["elephant_bought"]:
            sessionStorage[user_id] = {
                "suggests": [
                    "Не хочу.",
                    "Не буду.",
                    "Отстань!",
                ],
                "elephant_bought": True,
            }
            res["response"]["text"] = "Слона можно найти на Яндекс.Маркете! Купи теперь кролика!"
            res["response"]["buttons"] = get_suggests(user_id)
        else:
            res["response"]["text"] = "Кролика можно найти на Яндекс.Маркете!"
            res["response"]["end_session"] = True
        return

    if not sessionStorage[user_id]["elephant_bought"]:
        res["response"]["text"] = (
            f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
        )
    else:
        res["response"]["text"] = (
            f"Все говорят '{req['request']['original_utterance']}', а ты купи кролика!"
        )
    res["response"]["buttons"] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [{"title": suggest, "hide": True} for suggest in session["suggests"][:2]]

    session["suggests"] = session["suggests"][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        if not sessionStorage[user_id]["elephant_bought"]:
            suggests.append(
                {
                    "title": "Ладно",
                    "url": "https://market.yandex.ru/search?text=слон",
                    "hide": True,
                }
            )
        else:
            suggests.append(
                {
                    "title": "Ладно",
                    "url": "https://market.yandex.ru/search?text=кролик",
                    "hide": True,
                }
            )

    return suggests


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port)
    waitress.serve(app, host="0.0.0.0", port=port)
