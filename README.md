# Crawler
The crawler for WaveGenAI

## Setup

1. Install the required packages
```bash
pip install -r requirements.txt
```

2. Install docker

## Usage

Run the proxy
```bash
docker run -d --rm -it -p 3128:3128 -p 4444:4444 -e "TOR_INSTANCES=40" zhaowde/rotating-tor-http-proxy
```

Run the crawler
```bash
python main.py --csv --input FILE.txt --overwrite --file_name FILE.csv --num_processes 40
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details