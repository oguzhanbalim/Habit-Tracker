import json
import datetime
from collections import defaultdict

class Habit:
    def __init__(self, name, periodicity, created_at=None):
        self.name = name
        self.periodicity = periodicity
        self.created_at = created_at if created_at else datetime.datetime.now()
        self.checkoffs = []
        self.streak = 0
        self.last_checkoff_date = None

    def checkoff(self):
        today = datetime.date.today()
        if self.last_checkoff_date:
            delta = (today - self.last_checkoff_date).days
            if delta > self.periodicity:
                self.streak = 0
        self.checkoffs.append(datetime.datetime.now())
        self.last_checkoff_date = today
        self.streak += 1

    def current_streak(self):
        today = datetime.date.today()
        if self.last_checkoff_date:
            delta = (today - self.last_checkoff_date).days
            if delta <= self.periodicity:
                return self.streak
        return 0

    def longest_streak(self):
        if not self.checkoffs:
            return 0

        streaks = []
        current_streak = 1

        for i in range(1, len(self.checkoffs)):
            if (self.checkoffs[i].date() - self.checkoffs[i - 1].date()).days <= self.periodicity:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1

        streaks.append(current_streak)
        return max(streaks)

    def to_dict(self):
        return {
            "name": self.name,
            "periodicity": self.periodicity,
            "created_at": self.created_at.isoformat(),
            "checkoffs": [dt.isoformat() for dt in self.checkoffs]
        }

    @classmethod
    def from_dict(cls, data):
        habit = cls(data["name"], data["periodicity"], datetime.datetime.fromisoformat(data["created_at"]))
        habit.checkoffs = [datetime.datetime.fromisoformat(dt) for dt in data["checkoffs"]]
        if habit.checkoffs:
            habit.last_checkoff_date = habit.checkoffs[-1].date()
        return habit


class HabitTracker:
    def __init__(self):
        self.habits = {}
        self.habits_by_periodicity = defaultdict(list)

    def add_habit(self, name, periodicity):
        habit = Habit(name, periodicity)
        self.habits[name] = habit
        self.habits_by_periodicity[periodicity].append(habit)

    def delete_habit(self, name):
        if name in self.habits:
            habit = self.habits.pop(name)
            self.habits_by_periodicity[habit.periodicity].remove(habit)

    def checkoff_habit(self, name):
        if name in self.habits:
            self.habits[name].checkoff()
        else:
            print(f"Habit '{name}' does not exist.")

    def get_all_habits(self):
        return list(self.habits.values())

    def get_habits_by_periodicity(self, periodicity):
        return self.habits_by_periodicity[periodicity]

    def longest_streak_all(self):
        return max((habit.longest_streak() for habit in self.habits.values()), default=0)

    def longest_streak_for_habit(self, name):
        if name in self.habits:
            return self.habits[name].longest_streak()
        return 0

    def habits_struggled_last_month(self):
        one_month_ago = datetime.date.today() - datetime.timedelta(days=30)
        struggled_habits = []
        for habit in self.habits.values():
            if not habit.checkoffs or habit.checkoffs[-1].date() < one_month_ago:
                struggled_habits.append(habit.name)
        return struggled_habits

    def save_to_file(self, filename="habits.json"):
        with open(filename, "w") as f:
            json.dump({name: habit.to_dict() for name, habit in self.habits.items()}, f)

    def load_from_file(self, filename="habits.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.habits = {name: Habit.from_dict(h) for name, h in data.items()}
                self.habits_by_periodicity = defaultdict(list)
                for habit in self.habits.values():
                    self.habits_by_periodicity[habit.periodicity].append(habit)
        except FileNotFoundError:
            pass


def get_user_input(prompt, valid_responses):
    while True:
        response = input(prompt).strip().lower()
        if response in valid_responses:
            return response
        print(f"Please enter one of the following: {', '.join(valid_responses)}")

def cli():
    habit_tracker = HabitTracker()
    habit_tracker.load_from_file()

    predefined_habits = [
        {"name": "Read 10 Pages", "periodicity": 1, "checkoffs": ["2023-07-01", "2023-07-02", "2023-07-03", "2023-07-04", "2023-07-05", "2023-07-06", "2023-07-07"]},
        {"name": "Exercise", "periodicity": 1, "checkoffs": ["2023-07-01", "2023-07-02", "2023-07-03", "2023-07-05", "2023-07-06", "2023-07-07"]},
        {"name": "Drink 2.5 Liters of Water", "periodicity": 1, "checkoffs": ["2023-07-01", "2023-07-02", "2023-07-04", "2023-07-05", "2023-07-06"]},
        {"name": "Meditate for 10 Minutes", "periodicity": 1, "checkoffs": ["2023-07-01", "2023-07-03", "2023-07-04", "2023-07-06"]},
        {"name": "Weekly Review", "periodicity": 7, "checkoffs": ["2023-06-30"]}
    ]

    for habit_data in predefined_habits:
        habit = Habit(habit_data["name"], habit_data["periodicity"])
        habit.checkoffs = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in habit_data["checkoffs"]]
        if habit.checkoffs:
            habit.last_checkoff_date = habit.checkoffs[-1].date()
        habit_tracker.habits[habit.name] = habit
        habit_tracker.habits_by_periodicity[habit.periodicity].append(habit)

    user_name = input("What's your name? ").strip()
    print(f"Hello {user_name}, another brick on the wall, let's see how much we got closer to our aims.")

    questions = [
        "Did you read 10 pages today? ",
        "Did you exercise today? ",
        "Did you drink 2.5 liters of water today? ",
        "Did you meditate for 10 minutes today? ",
        "Did you review your week? "
    ]

    completed = 0
    total = len(questions)

    for question in questions:
        response = get_user_input(question, ["yes", "no"])
        if response == "yes":
            completed += 1

    score = f"{completed} / {total}"
    print(f"\nOverall Score: {score}")
    if completed < total:
        print(f"Habits missed: {total - completed}")
        print("Don't forget why you started, you will make it happen. Work for it. You got this", user_name, "!")

    if completed <= 3:
        print("Keep pushing forward! You can do this.")
    elif completed <= 6:
        print("Good job! Keep working on your habits.")
    elif completed <= 9:
        print("Great work! You're doing amazing.")
    else:
        print("Perfect score! You nailed it!")

    while True:
        print("\nOptions:")
        print("1. List all habits")
        print("2. List habits by periodicity")
        print("3. Check off a habit")
        print("4. Add a new habit")
        print("5. Delete a habit")
        print("6. View longest streaks")
        print("7. Analyse habits")
        print("8. Exit and save")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            habits = habit_tracker.get_all_habits()
            for habit in habits:
                print(f"- {habit.name} (Periodicity: {habit.periodicity} days)")

        elif choice == "2":
            periodicity = int(input("Enter periodicity (in days): ").strip())
            habits = habit_tracker.get_habits_by_periodicity(periodicity)
            for habit in habits:
                print(f"- {habit.name}")

        elif choice == "3":
            habit_name = input("Enter habit name to check off: ").strip()
            habit_tracker.checkoff_habit(habit_name)

        elif choice == "4":
            habit_name = input("Enter new habit name: ").strip()
            periodicity = int(input("Enter periodicity (in days): ").strip())
            habit_tracker.add_habit(habit_name, periodicity)

        elif choice == "5":
            habit_name = input("Enter habit name to delete: ").strip()
            habit_tracker.delete_habit(habit_name)

        elif choice == "6":
            habit_name = input("Enter habit name to view longest streak (or leave blank for all): ").strip()
            if habit_name:
                streak = habit_tracker.longest_streak_for_habit(habit_name)
                print(f"Longest streak for {habit_name}: {streak} days")
            else:
                streak = habit_tracker.longest_streak_all()
                print(f"Longest streak for all habits: {streak} days")

        elif choice == "7":
            print("Analyzing habits:")
            longest_streak = habit_tracker.longest_streak_all()
            current_daily_habits = [habit.name for habit in habit_tracker.get_habits_by_periodicity(1)]
            struggled_habits = habit_tracker.habits_struggled_last_month()
            print(f"Longest streak: {longest_streak} days")
            print("Current daily habits:", ", ".join(current_daily_habits))
            print("Habits struggled most last month:", ", ".join(struggled_habits))

        elif choice == "8":
            habit_tracker.save_to_file()
            print("Habits saved. Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

def run():
    cli()

if __name__ == "__main__":
    run()
