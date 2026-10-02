from flask import Flask, jsonify, request

app = Flask(__name__)

# Stockage en mémoire (suffisant pour la démo)
items = []


def compute_total(prices):
    """Fonction métier testée unitairement : somme des prix arrondie à 2 décimales."""
    if any(p < 0 for p in prices):
        raise ValueError("Un prix ne peut pas être négatif")
    return round(sum(prices), 2)


@app.route("/")
def home():
    return "<h1>MyApp</h1><p>Application déployée automatiquement via GitHub Actions.</p>"


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/items", methods=["GET"])
def list_items():
    return jsonify(items)


@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json(silent=True) or {}
    if "name" not in data or "price" not in data:
        return jsonify({"error": "name et price sont obligatoires"}), 400
    item = {"id": len(items) + 1, "name": data["name"], "price": float(data["price"])}
    items.append(item)
    return jsonify(item), 201


@app.route("/total")
def total():
    return jsonify({"total": compute_total([i["price"] for i in items])})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8016)
