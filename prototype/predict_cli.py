#!/usr/bin/env python3
"""
predict_cli.py — command-line wrapper around predict.py, for scripting/batch
use alongside Regression_GUI.py.

    python predict_cli.py --year 2012 --month 8 --day 15 --hour 8 \
        --temp 28.5 --humidity 55 --windspeed 12 --holiday 0 --workingday 1 \
        --weather 1 --season 3
"""
import argparse
from predict import predict


def main():
    parser = argparse.ArgumentParser(description="Predict hourly bike rental demand.")
    parser.add_argument("--year", type=int, required=True, choices=[2011, 2012])
    parser.add_argument("--month", type=int, required=True, choices=range(1, 13))
    parser.add_argument("--day", type=int, required=True, choices=range(1, 32))
    parser.add_argument("--hour", type=int, required=True, choices=range(0, 24))
    parser.add_argument("--temp", type=float, required=True)
    parser.add_argument("--humidity", type=float, required=True)
    parser.add_argument("--windspeed", type=float, required=True)
    parser.add_argument("--holiday", type=int, required=True, choices=[0, 1])
    parser.add_argument("--workingday", type=int, required=True, choices=[0, 1])
    parser.add_argument("--weather", type=int, required=True, choices=[1, 2, 3, 4])
    parser.add_argument("--season", type=int, required=True, choices=[1, 2, 3, 4])
    args = parser.parse_args()

    data = {
        "year": args.year, "month": args.month, "day": args.day, "hour": args.hour,
        "temp": args.temp, "humidity": args.humidity, "windspeed": args.windspeed,
        "holiday": args.holiday, "workingday": args.workingday,
    }
    for w in (1, 2, 3, 4):
        data[f"weather_{w}"] = (args.weather == w)
    for s in (1, 2, 3, 4):
        data[f"season_{s}"] = (args.season == s)

    print(f"Predicted bike rentals for that hour: {predict(data)}")


if __name__ == "__main__":
    main()
