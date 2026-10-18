import argparse

from app import create_app
from app.config import PORTS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=sorted(PORTS), default="en")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    app = create_app(args.lang)
    app.run(host=args.host, port=args.port or PORTS[args.lang], debug=False)


if __name__ == "__main__":
    main()
