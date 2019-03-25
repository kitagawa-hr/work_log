import calendar
import datetime
import subprocess

import pandas as pd


WEEKDAY = "月火水木金土日"


def get_sleep_logs(year, month):
    if month < 10:
        month_str = "0" + str(month)
    else:
        month_str = str(month)
    p1 = subprocess.Popen(["pmset", "-g", "log"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(
        ["grep", "Kernel Idle sleep preventers"],
        stdin=p1.stdout,
        stdout=subprocess.PIPE,
    )
    p3 = subprocess.Popen(
        ["grep", f"{year}-{month_str}-"], stdin=p2.stdout, stdout=subprocess.PIPE
    )
    p4 = subprocess.Popen(
        ["awk", "{print $1, $2}"], stdin=p3.stdout, stdout=subprocess.PIPE
    )
    p1.stdout.close()
    p2.stdout.close()
    p3.stdout.close()
    output = p4.communicate()[0]
    sleep_logs_str = output.decode("utf-8").split("\n")
    sleep_logs = [
        datetime.datetime.strptime(log, "%Y-%m-%d %H:%M:%S")
        for log in sleep_logs_str
        if log
    ]
    return sleep_logs


def get_loginout_log(year, month, in_or_out="in"):
    month_en = calendar.month_abbr[month]
    if in_or_out == "in":
        arg = "reboot"
    else:
        arg = "shutdown"

    p1 = subprocess.Popen(["last", arg], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", month_en], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(
        ["awk", "{print $5, $6}"], stdin=p2.stdout, stdout=subprocess.PIPE
    )
    output = p3.communicate()[0]
    logs_str = output.decode("utf-8").split("\n")
    logs = [
        datetime.datetime.strptime(f"{year}-{month}-" + log, "%Y-%m-%d %H:%M")
        for log in logs_str
        if log
    ]
    return logs


def last_day_of_month(year, month):
    next_month = datetime.datetime(year, month + 1, 1)
    return (next_month - datetime.timedelta(days=next_month.day)).day


def take_if_exists(lis, index):
    try:
        return lis[index]
    except IndexError:
        return None


def minmax_datetime(min_or_max, *dates):
    try:
        return min_or_max([date for date in dates if date])
    except ValueError:
        return None


def make_summary(year, month):
    login_logs = get_loginout_log(year, month, "in")
    logout_logs = get_loginout_log(year, month, "out")
    sleep_logs = get_sleep_logs(year, month)
    date_range = pd.date_range(
        datetime.datetime(year, month, 1),
        datetime.datetime(year, month, last_day_of_month(year, month)),
    )
    login_first = {
        date: take_if_exists(
            [log for log in login_logs if log.day == date.date().day], 0
        )
        for date in date_range
    }
    logout_last = {
        date: take_if_exists(
            [log for log in logout_logs if log.day == date.date().day], -1
        )
        for date in date_range
    }
    sleep_first = {
        date: take_if_exists(
            [log for log in sleep_logs if log.day == date.date().day], 0
        )
        for date in date_range
    }
    sleep_last = {
        date: take_if_exists(
            [log for log in sleep_logs if log.day == date.date().day], -1
        )
        for date in date_range
    }
    summary = pd.DataFrame({"date": date_range})
    summary["login_first"] = login_first.values()
    summary["logout_last"] = logout_last.values()
    summary["sleep_first"] = sleep_first.values()
    summary["sleep_last"] = sleep_last.values()
    summary["start"] = [
        minmax_datetime(min, a, b)
        for a, b in zip(summary["login_first"], summary["sleep_first"])
    ]
    summary["end"] = [
        minmax_datetime(max, a, b)
        for a, b in zip(summary["logout_last"], summary["sleep_last"])
    ]
    return summary


def format_datetime(dt):
    if not dt or dt != dt:
        return None
    return f"{int(dt.hour)}:{dt.minute // 10 * 10}"


if __name__ == "__main__":
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    summary = make_summary(year, month)
    formatted = pd.DataFrame()
    formatted["月"] = month
    formatted["日"] = summary["date"].dt.day
    formatted["曜日"] = summary["date"].dt.date.apply(lambda x: WEEKDAY[x.weekday()])
    formatted["勤務開始時間"] = summary["start"].apply(format_datetime)
    formatted["勤務終了時間"] = summary["end"].apply(format_datetime)
    formatted.to_csv(f"{year}年{month}月.csv", index=False, encoding="cp932", mode="a")
