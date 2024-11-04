import argparse
from datetime import datetime, timedelta
import calendar

def calculate_timesteps(start_date, end_date, timestep):
    total_seconds = (end_date - start_date).total_seconds() + 1  # Add 1 to include the last second
    return int(total_seconds / timestep)

def format_duration(start_date, end_date):
    duration = end_date - start_date
    years = duration.days // 365 
    remaining_days = duration.days % 365 
    months = 0 
    
    temp_date = start_date.replace(year=start_date.year + years)
    while temp_date + timedelta(days=calendar.monthrange(temp_date.year, temp_date.month)[1]) <= end_date:
        months += 1
        temp_date = (temp_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    
    remaining_days = (end_date - temp_date).days + 1 

    return f"{years} years, {months} months, and {remaining_days} days"

def parse_date(date_str, is_end_date=False):
    try:
        parts = date_str.split('-')
        if len(parts) == 1:  # Only year provided
            year = int(parts[0])
            if is_end_date:
                return datetime(year, 12, 31, 23, 59, 59) 
            else:
                return datetime(year, 1, 1)
        elif len(parts) == 2:  # Year and month provided
            year, month = map(int, parts)
            # Validate month
            if not 1 <= month <= 12:
                raise argparse.ArgumentTypeError(f"Invalid month: {month}. Month must be between 1 and 12.")
            if is_end_date:
                last_day = calendar.monthrange(year, month)[1]
                return datetime(year, month, last_day, 23, 59, 59) 
            else:
                return datetime(year, month, 1)
        elif len(parts) == 3:  # Year, month, and day provided
            year, month, day = map(int, parts)
            # Validate month
            if not 1 <= month <= 12:
                raise argparse.ArgumentTypeError(f"Invalid month: {month}. Month must be between 1 and 12.")
            # Validate day
            last_day_of_month = calendar.monthrange(year, month)[1]
            if not 1 <= day <= last_day_of_month:
                raise argparse.ArgumentTypeError(
                    f"Invalid day: {day}. {calendar.month_name[month]} {year} has {last_day_of_month} days."
                )
            if is_end_date:
                return datetime(year, month, day, 23, 59, 59) 
            else:
                return datetime(year, month, day)
        else:
            raise ValueError
    except ValueError as e:
        if "day is out of range for month" in str(e):
            month_name = calendar.month_name[int(parts[1])]
            last_day = calendar.monthrange(int(parts[0]), int(parts[1]))[1]
            raise argparse.ArgumentTypeError(
                f"Invalid date: {date_str}. {month_name} has {last_day} days."
            )
        raise argparse.ArgumentTypeError("Invalid date format. Use YYYY, YYYY-MM, or YYYY-MM-DD")

def main():
    parser = argparse.ArgumentParser(description="Calculate number of model timesteps.")
    parser.add_argument("start_date", type=lambda x: parse_date(x, False), help="Start date for the model (YYYY, YYYY-MM, or YYYY-MM-DD)")
    parser.add_argument("end_date", type=lambda x: parse_date(x, True), help="End date for the model (YYYY, YYYY-MM, or YYYY-MM-DD)")
    parser.add_argument("--timestep", type=int, default=400, help="Timestep in seconds (default: 400)")

    args = parser.parse_args()

    if args.start_date > args.end_date:
        print("Error: Start date must be before end date.")
        return

    num_timesteps = calculate_timesteps(args.start_date, args.end_date, args.timestep)
    duration = format_duration(args.start_date, args.end_date)

    print(f"Number of timesteps: {num_timesteps}")
    print(f"Start date: {args.start_date.strftime('%Y-%m-%d')}")
    print(f"End date: {args.end_date.strftime('%Y-%m-%d')}")
    print(f"Total duration: {duration}")

if __name__ == "__main__":
    main()
