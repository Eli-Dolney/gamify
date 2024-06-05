import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog, Text, END
import time
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk


class GamifyLifeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gamify Your Life")
        self.geometry("1280x720")
        ctk.set_appearance_mode("system")

        self.categories = {}
        self.activity_start_times = {}
        self.activity_labels = {}
        self.activity_progress_bars = {}
        self.activity_progress_labels = {}
        self.activity_goals = {}
        self.activity_sessions = {}
        self.milestones = [1, 10, 100, 1000, 10000]  # Hours
        self.milestones_reached = {}
        self.tasks = []
        self.goals = []
        self.vision_board = []

        self.create_widgets()
        self.load_data()
        self.show_dashboard()

    def create_widgets(self):
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self.dashboard_button = ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard)
        self.dashboard_button.pack(pady=10)

        self.categories_button = ctk.CTkButton(self.sidebar, text="Manage Categories", command=self.show_categories)
        self.categories_button.pack(pady=10)

        self.statistics_button = ctk.CTkButton(self.sidebar, text="Statistics", command=self.show_statistics)
        self.statistics_button.pack(pady=10)

        self.tasks_button = ctk.CTkButton(self.sidebar, text="Tasks", command=self.show_tasks)
        self.tasks_button.pack(pady=10)

        self.goals_button = ctk.CTkButton(self.sidebar, text="Goals", command=self.show_goals)
        self.goals_button.pack(pady=10)

        self.vision_board_button = ctk.CTkButton(self.sidebar, text="Vision Board", command=self.show_vision_board)
        self.vision_board_button.pack(pady=10)

        self.exit_button = ctk.CTkButton(self.sidebar, text="Exit", command=self.exit_app)
        self.exit_button.pack(pady=10)

    def show_dashboard(self):
        self.clear_content()
        title_label = ctk.CTkLabel(self.content, text="Gamify Your Life Dashboard", font=("Arial", 24, "bold"))
        title_label.pack(pady=10)
        dashboard_frame = ctk.CTkFrame(self.content)
        dashboard_frame.pack(fill="both", expand=True)
        self.create_dashboard_content(dashboard_frame)

    def create_dashboard_content(self, parent_frame):
        categories = list(self.categories.keys())
        if not categories:
            label = ctk.CTkLabel(parent_frame, text="No categories available. Please add categories.", font=("Arial", 18))
            label.pack(pady=20)
            return

        for category in categories:
            category_frame = ctk.CTkFrame(parent_frame)
            category_frame.pack(fill="x", pady=10)

            category_label = ctk.CTkLabel(category_frame, text=f"{category.capitalize()} Progress", font=("Arial", 18))
            category_label.pack(pady=5)

            activities = list(self.categories[category].keys())
            for activity in activities:
                activity_frame = ctk.CTkFrame(category_frame)
                activity_frame.pack(fill="x", pady=5)

                activity_label = ctk.CTkLabel(activity_frame, text=f"{activity.capitalize()}", font=("Arial", 14))
                activity_label.pack(side="left", padx=5)
                
                self.activity_labels[f"{category}_{activity}_label"] = ctk.CTkLabel(activity_frame, text="")
                self.activity_labels[f"{category}_{activity}_label"].pack(side="left", padx=5)
                
                self.activity_progress_bars[f"{category}_{activity}_progress_bar"] = ctk.CTkProgressBar(activity_frame, mode='determinate')
                self.activity_progress_bars[f"{category}_{activity}_progress_bar"].pack(side="left", padx=5, fill="x", expand=True)
                
                self.activity_progress_labels[f"{category}_{activity}_progress_label"] = ctk.CTkLabel(activity_frame, text="")
                self.activity_progress_labels[f"{category}_{activity}_progress_label"].pack(side="left", padx=5)
                
                self.update_activity_display(category, activity, self.categories[category][activity])

        self.create_dashboard_graphs(parent_frame)
        self.create_stats_chart(parent_frame)

    def create_dashboard_graphs(self, parent_frame):
        if not self.categories:
            return

        fig, ax = plt.subplots(1, 2, figsize=(14, 6))

        categories = list(self.categories.keys())
        total_times = [sum(self.categories[cat].values()) / 3600 for cat in categories]  # Convert to hours

        # Bar Graph
        ax[0].barh(categories, total_times, color='skyblue')
        ax[0].set_xlabel('Total Hours')
        ax[0].set_title('Total Hours Spent per Category')

        # Pie Chart
        ax[1].pie(total_times, labels=categories, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
        ax[1].set_title('Distribution of Total Hours per Category')

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

    def create_stats_chart(self, parent_frame):
        if not self.categories:
            return

        activities = list(self.categories.keys())
        if not activities:
            return

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        metrics = ["Total Hours", "Sessions", "Avg Hours/Session", "Goal Progress"]
        num_vars = len(metrics)

        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        def get_metric_values(activity):
            total_time = sum(self.categories[activity].values()) / 3600  # Convert to hours
            sessions = sum(self.activity_sessions.get(act, 0) for act in self.categories[activity])
            avg_time_per_session = (total_time / sessions) if sessions > 0 else 0
            goal_progress = (total_time / (self.activity_goals.get(activity, 1) / 3600)) * 100

            return [total_time, sessions, avg_time_per_session, goal_progress]

        stats = [get_metric_values(activity) for activity in activities]
        stats = np.array(stats)
        stats = np.mean(stats, axis=0).tolist()
        stats += stats[:1]

        ax.fill(angles, stats, color='blue', alpha=0.25)
        ax.plot(angles, stats, color='blue', linewidth=2)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

    def show_categories(self):
        self.clear_content()

        categories_frame = ctk.CTkFrame(self.content)
        categories_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(categories_frame, text="Manage Categories", font=("Arial", 24))
        label.pack(pady=20)

        new_category_label = ctk.CTkLabel(categories_frame, text="New Category Name:", font=("Arial", 14))
        new_category_label.pack(pady=5)
        self.new_category_entry = ctk.CTkEntry(categories_frame)
        self.new_category_entry.pack(pady=5)

        add_category_btn = ctk.CTkButton(categories_frame, text="Add Category", command=self.add_category)
        add_category_btn.pack(pady=10)

        self.categories_list_frame = ctk.CTkFrame(categories_frame)
        self.categories_list_frame.pack(fill="both", expand=True)

        self.update_categories_list()

    def add_category(self):
        new_category = self.new_category_entry.get().strip()
        if new_category and new_category not in self.categories:
            self.categories[new_category] = {}
            self.update_categories_list()
            self.save_data()

    def update_categories_list(self):
        for widget in self.categories_list_frame.winfo_children():
            widget.destroy()

        for category in self.categories.keys():
            frame = ctk.CTkFrame(self.categories_list_frame)
            frame.pack(fill="x", pady=5)

            label = ctk.CTkLabel(frame, text=category, font=("Arial", 14))
            label.pack(side="left", padx=10)

            manage_btn = ctk.CTkButton(frame, text="Manage", command=lambda c=category: self.show_activities(c))
            manage_btn.pack(side="right", padx=10)

            delete_btn = ctk.CTkButton(frame, text="Delete", command=lambda c=category: self.delete_category(c))
            delete_btn.pack(side="right", padx=10)

    def delete_category(self, category):
        if category in self.categories:
            del self.categories[category]
            self.update_categories_list()
            self.save_data()

    def show_activities(self, category):
        self.clear_content()

        activities_frame = ctk.CTkFrame(self.content)
        activities_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(activities_frame, text=f"Manage Activities for {category.capitalize()}", font=("Arial", 24))
        label.pack(pady=20)

        new_activity_label = ctk.CTkLabel(activities_frame, text="New Activity Name:", font=("Arial", 14))
        new_activity_label.pack(pady=5)
        self.new_activity_entry = ctk.CTkEntry(activities_frame)
        self.new_activity_entry.pack(pady=5)

        add_activity_btn = ctk.CTkButton(activities_frame, text="Add Activity", command=lambda: self.add_activity(category))
        add_activity_btn.pack(pady=10)

        self.activities_list_frame = ctk.CTkFrame(activities_frame)
        self.activities_list_frame.pack(fill="both", expand=True)

        self.update_activities_list(category)

    def add_activity(self, category):
        new_activity = self.new_activity_entry.get().strip()
        if new_activity and new_activity not in self.categories[category]:
            self.categories[category][new_activity] = 0
            self.activity_start_times[new_activity] = None
            self.activity_goals[new_activity] = 3600  # Default goal is 1 hour to avoid division by zero
            self.activity_sessions[new_activity] = 0  # Track number of sessions
            self.milestones_reached[new_activity] = []
            self.update_activities_list(category)
            self.save_data()

    def update_activities_list(self, category):
        for widget in self.activities_list_frame.winfo_children():
            widget.destroy()

        for activity in self.categories[category].keys():
            frame = ctk.CTkFrame(self.activities_list_frame)
            frame.pack(fill="x", pady=5)

            label = ctk.CTkLabel(frame, text=activity, font=("Arial", 14))
            label.pack(side="left", padx=10)

            start_btn = ctk.CTkButton(frame, text="Start", command=lambda a=activity: self.start_activity(category, a))
            start_btn.pack(side="right", padx=5)

            stop_btn = ctk.CTkButton(frame, text="Stop", command=lambda a=activity: self.stop_activity(category, a))
            stop_btn.pack(side="right", padx=5)

            delete_btn = ctk.CTkButton(frame, text="Delete", command=lambda a=activity: self.delete_activity(category, a))
            delete_btn.pack(side="right", padx=10)

            goal_entry_label = ctk.CTkLabel(frame, text="Goal (hours):", font=("Arial", 14))
            goal_entry_label.pack(side="left", padx=5)
            goal_entry = ctk.CTkEntry(frame)
            goal_entry.pack(side="left", padx=5)
            set_goal_btn = ctk.CTkButton(frame, text="Set Goal", command=lambda a=activity, e=goal_entry: self.set_goal(a, e.get()))
            set_goal_btn.pack(side="left", padx=5)

            self.activity_labels[f"{category}_{activity}_label"] = ctk.CTkLabel(frame, text="")
            self.activity_labels[f"{category}_{activity}_label"].pack(pady=5)
            self.activity_progress_bars[f"{category}_{activity}_progress_bar"] = ctk.CTkProgressBar(frame, mode='determinate')
            self.activity_progress_bars[f"{category}_{activity}_progress_bar"].pack(pady=5, fill="x", expand=True)
            self.activity_progress_labels[f"{category}_{activity}_progress_label"] = ctk.CTkLabel(frame, text=f"{activity.replace('_', ' ').capitalize()} Progress: 0%", font=("Arial", 14))
            self.activity_progress_labels[f"{category}_{activity}_progress_label"].pack(pady=5)

    def delete_activity(self, category, activity):
        if activity in self.categories[category]:
            del self.categories[category][activity]
            self.update_activities_list(category)
            self.save_data()

    def set_goal(self, activity, goal):
        try:
            goal_hours = float(goal)
            self.activity_goals[activity] = goal_hours * 3600  # Convert hours to seconds
            self.save_data()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the goal.")

    def start_activity(self, category, activity):
        self.activity_start_times[activity] = time.time()
        if activity not in self.activity_sessions:
            self.activity_sessions[activity] = 0
        self.activity_sessions[activity] += 1
        self.update_activity_timer(category, activity)

    def stop_activity(self, category, activity):
        start_time = self.activity_start_times[activity]
        if start_time is not None:
            elapsed = time.time() - start_time
            self.categories[category][activity] += elapsed
            self.activity_start_times[activity] = None
            self.update_label(category, activity)
            self.check_milestones(activity, self.categories[category][activity])
            self.save_data()

    def update_activity_timer(self, category, activity):
        start_time = self.activity_start_times[activity]
        if start_time is not None:
            elapsed = time.time() - start_time
            total_time = self.categories[category][activity] + elapsed
            self.update_activity_display(category, activity, total_time)
            self.after(1000, lambda: self.update_activity_timer(category, activity))

    def update_activity_display(self, category, activity, total_time):
        hours, rem = divmod(total_time, 3600)
        minutes, seconds = divmod(rem, 60)
        self.activity_labels[f"{category}_{activity}_label"].configure(text=f"{activity.replace('_', ' ').capitalize()} Time: {int(hours)}h {int(minutes)}m {int(seconds)}s")
        goal_time = self.activity_goals.get(activity, 1)  # Avoid division by zero
        progress_percentage = (total_time / goal_time) * 100 if goal_time > 0 else 0
        self.activity_progress_bars[f"{category}_{activity}_progress_bar"]['value'] = progress_percentage
        self.activity_progress_labels[f"{category}_{activity}_progress_label"].configure(text=f"{activity.replace('_', ' ').capitalize()} Progress: {progress_percentage:.2f}%")

    def update_label(self, category, activity):
        total_time = self.categories[category][activity]
        self.update_activity_display(category, activity, total_time)

    def check_milestones(self, activity, total_time):
        hours = total_time / 3600
        for milestone in self.milestones:
            if hours >= milestone and milestone not in self.milestones_reached[activity]:
                self.milestones_reached[activity].append(milestone)
                messagebox.showinfo("Milestone Reached", f"Congratulations! You've reached {milestone} hours in {activity.replace('_', ' ').capitalize()}!")

        if activity in self.activity_goals and total_time >= self.activity_goals[activity]:
            messagebox.showinfo("Goal Achieved", f"Great job! You've achieved your goal for {activity.replace('_', ' ').capitalize()}!")

    def show_statistics(self):
        self.clear_content()

        statistics_frame = ctk.CTkFrame(self.content)
        statistics_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(statistics_frame, text="Statistics", font=("Arial", 24))
        label.pack(pady=20)

        # Tier Key
        tiers_frame = ctk.CTkFrame(statistics_frame)
        tiers_frame.pack(fill="x", pady=10)
        tier_labels = [
            ("Master (100,000+ hours)", "green"),
            ("Expert (50,000 - 99,999 hours)", "yellow"),
            ("Pro (10,000 - 49,999 hours)", "orange"),
            ("Intermediate (1,000 - 9,999 hours)", "purple"),
            ("Beginner (100 - 999 hours)", "blue"),
            ("Noob (0 - 99 hours)", "red")
        ]
        for tier, color in tier_labels:
            tier_label = ctk.CTkLabel(tiers_frame, text=tier, fg_color=color, width=200)
            tier_label.pack(side="left", padx=10, pady=5)

        # Display detailed statistics
        for category, activities in self.categories.items():
            category_label = ctk.CTkLabel(statistics_frame, text=f"{category.capitalize()} Statistics", font=("Arial", 18))
            category_label.pack(pady=10)
            for activity, total_time in activities.items():
                hours, rem = divmod(total_time, 3600)
                minutes, seconds = divmod(rem, 60)
                tier, color = self.get_tier_and_color(total_time)
                sessions = self.activity_sessions.get(activity, 0)
                average_time = total_time / sessions if sessions > 0 else 0
                avg_hours, avg_rem = divmod(average_time, 3600)
                avg_minutes, avg_seconds = divmod(avg_rem, 60)
                progress_percentage = (total_time / self.activity_goals.get(activity, 1)) * 100 if self.activity_goals.get(activity, 1) > 0 else 0
                activity_label = ctk.CTkLabel(
                    statistics_frame, 
                    text=(
                        f"{activity.replace('_', ' ').capitalize()}: {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
                        f"Tier: {tier}\n"
                        f"Sessions: {sessions}\n"
                        f"Average Time per Session: {int(avg_hours)}h {int(avg_minutes)}m {int(avg_seconds)}s\n"
                        f"Goal Progress: {progress_percentage:.2f}%"
                    ), 
                    fg_color=color
                )
                activity_label.pack(pady=5)

    def get_tier_and_color(self, total_time):
        tiers = [
            (360000000, "Master", "green"),  # 100,000 hours
            (180000000, "Expert", "yellow"),  # 50,000 hours
            (36000000, "Pro", "orange"),  # 10,000 hours
            (3600000, "Intermediate", "purple"),  # 1,000 hours
            (360000, "Beginner", "blue"),  # 100 hours
            (0, "Noob", "red")  # 0 hours
        ]
        for threshold, tier, color in tiers:
            if total_time >= threshold:
                return tier, color
        return "Noob", "red"

    def show_tasks(self):
        self.clear_content()

        tasks_frame = ctk.CTkFrame(self.content)
        tasks_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(tasks_frame, text="Task List", font=("Arial", 24))
        label.pack(pady=20)

        new_task_label = ctk.CTkLabel(tasks_frame, text="New Task:", font=("Arial", 14))
        new_task_label.pack(pady=5)
        self.new_task_entry = ctk.CTkEntry(tasks_frame)
        self.new_task_entry.pack(pady=5)

        add_task_btn = ctk.CTkButton(tasks_frame, text="Add Task", command=self.add_task)
        add_task_btn.pack(pady=10)

        self.tasks_list_frame = ctk.CTkFrame(tasks_frame)
        self.tasks_list_frame.pack(fill="both", expand=True)

        self.update_tasks_list()

    def add_task(self):
        new_task = self.new_task_entry.get().strip()
        if new_task:
            self.tasks.append({"task": new_task, "completed": False})
            self.update_tasks_list()
            self.save_data()

    def update_tasks_list(self):
        for widget in self.tasks_list_frame.winfo_children():
            widget.destroy()

        for idx, task in enumerate(self.tasks):
            frame = ctk.CTkFrame(self.tasks_list_frame)
            frame.pack(fill="x", pady=5)

            task_text = task["task"]
            if task["completed"]:
                task_text += " (Completed)"
                label = ctk.CTkLabel(frame, text=task_text, font=("Arial", 14), fg_color="green")
            else:
                label = ctk.CTkLabel(frame, text=task_text, font=("Arial", 14))

            label.pack(side="left", padx=10)

            complete_btn = ctk.CTkButton(frame, text="Complete", command=lambda idx=idx: self.complete_task(idx))
            complete_btn.pack(side="right", padx=5)

            delete_btn = ctk.CTkButton(frame, text="Delete", command=lambda idx=idx: self.delete_task(idx))
            delete_btn.pack(side="right", padx=5)

    def complete_task(self, idx):
        self.tasks[idx]["completed"] = True
        self.update_tasks_list()
        self.save_data()

    def delete_task(self, idx):
        del self.tasks[idx]
        self.update_tasks_list()
        self.save_data()

    def show_goals(self):
        self.clear_content()

        goals_frame = ctk.CTkFrame(self.content)
        goals_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(goals_frame, text="Goal List", font=("Arial", 24))
        label.pack(pady=20)

        new_goal_label = ctk.CTkLabel(goals_frame, text="New Goal:", font=("Arial", 14))
        new_goal_label.pack(pady=5)
        self.new_goal_entry = ctk.CTkEntry(goals_frame)
        self.new_goal_entry.pack(pady=5)

        add_goal_btn = ctk.CTkButton(goals_frame, text="Add Goal", command=self.add_goal)
        add_goal_btn.pack(pady=10)

        self.goals_list_frame = ctk.CTkFrame(goals_frame)
        self.goals_list_frame.pack(fill="both", expand=True)

        self.update_goals_list()

    def add_goal(self):
        new_goal = self.new_goal_entry.get().strip()
        if new_goal:
            self.goals.append({"goal": new_goal, "progress": 0})
            self.update_goals_list()
            self.save_data()

    def update_goals_list(self):
        for widget in self.goals_list_frame.winfo_children():
            widget.destroy()

        for idx, goal in enumerate(self.goals):
            frame = ctk.CTkFrame(self.goals_list_frame)
            frame.pack(fill="x", pady=5)

            goal_text = goal["goal"]
            label = ctk.CTkLabel(frame, text=goal_text, font=("Arial", 14))
            label.pack(side="left", padx=10)

            progress_label = ctk.CTkLabel(frame, text=f"Progress: {goal['progress']}%", font=("Arial", 14))
            progress_label.pack(side="left", padx=10)

            progress_entry = ctk.CTkEntry(frame, width=50)
            progress_entry.pack(side="left", padx=5)
            set_progress_btn = ctk.CTkButton(frame, text="Set Progress", command=lambda idx=idx, e=progress_entry: self.set_goal_progress(idx, e.get()))
            set_progress_btn.pack(side="left", padx=5)

            delete_btn = ctk.CTkButton(frame, text="Delete", command=lambda idx=idx: self.delete_goal(idx))
            delete_btn.pack(side="right", padx=10)

    def set_goal_progress(self, idx, progress):
        try:
            progress_value = int(progress)
            if 0 <= progress_value <= 100:
                self.goals[idx]["progress"] = progress_value
                self.update_goals_list()
                self.save_data()
            else:
                messagebox.showerror("Invalid Input", "Please enter a valid progress percentage (0-100).")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the progress.")

    def delete_goal(self, idx):
        del self.goals[idx]
        self.update_goals_list()
        self.save_data()

    def show_vision_board(self):
        self.clear_content()

        vision_board_frame = ctk.CTkFrame(self.content)
        vision_board_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(vision_board_frame, text="Vision Board", font=("Arial", 24))
        label.pack(pady=20)

        upload_image_btn = ctk.CTkButton(vision_board_frame, text="Upload Image", command=self.upload_image)
        upload_image_btn.pack(pady=10)

        self.vision_board_list_frame = ctk.CTkFrame(vision_board_frame)
        self.vision_board_list_frame.pack(fill="both", expand=True)

        self.update_vision_board_list()

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            description = self.simpledialog.askstring("Image Description", "Enter a description for the image:")
            if description:
                self.vision_board.append({"image_path": file_path, "description": description})
                self.update_vision_board_list()
                self.save_data()

    def update_vision_board_list(self):
        for widget in self.vision_board_list_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.vision_board):
            frame = ctk.CTkFrame(self.vision_board_list_frame)
            frame.pack(fill="x", pady=5)

            img = Image.open(item["image_path"])
            img.thumbnail((100, 100))
            img = ImageTk.PhotoImage(img)

            img_label = ctk.CTkLabel(frame, image=img)
            img_label.image = img  # Keep a reference to avoid garbage collection
            img_label.pack(side="left", padx=10)

            description_label = ctk.CTkLabel(frame, text=item["description"], font=("Arial", 14))
            description_label.pack(side="left", padx=10)

            delete_btn = ctk.CTkButton(frame, text="Delete", command=lambda idx=idx: self.delete_vision_board_item(idx))
            delete_btn.pack(side="right", padx=10)

    def delete_vision_board_item(self, idx):
        del self.vision_board[idx]
        self.update_vision_board_list()
        self.save_data()

    def get_tier_and_color(self, total_time):
        tiers = [
            (360000000, "Master", "green"),  # 100,000 hours
            (180000000, "Expert", "yellow"),  # 50,000 hours
            (36000000, "Pro", "orange"),  # 10,000 hours
            (3600000, "Intermediate", "purple"),  # 1,000 hours
            (360000, "Beginner", "blue"),  # 100 hours
            (0, "Noob", "red")  # 0 hours
        ]
        for threshold, tier, color in tiers:
            if total_time >= threshold:
                return tier, color
        return "Noob", "red"

    def load_data(self):
        if os.path.exists("timer_data.json"):
            with open("timer_data.json", "r") as file:
                data = json.load(file)
                self.categories = data.get("categories", {})
                self.activity_goals = data.get("activity_goals", {})
                self.activity_sessions = data.get("activity_sessions", {})
                self.milestones_reached = data.get("milestones_reached", {})
                self.tasks = data.get("tasks", [])
                self.goals = data.get("goals", [])
                self.vision_board = data.get("vision_board", [])
                for category in self.categories.keys():
                    for activity in self.categories[category].keys():
                        self.activity_start_times[activity] = None
                        if activity not in self.milestones_reached:
                            self.milestones_reached[activity] = []
                        if activity not in self.activity_sessions:
                            self.activity_sessions[activity] = 0

    def save_data(self):
        data = {
            "categories": self.categories,
            "activity_goals": self.activity_goals,
            "activity_sessions": self.activity_sessions,
            "milestones_reached": self.milestones_reached,
            "tasks": self.tasks,
            "goals": self.goals,
            "vision_board": self.vision_board
        }
        with open("timer_data.json", "w") as file:
            json.dump(data, file)

    def exit_app(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.save_data()
            self.destroy()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()


app = GamifyLifeApp()
app.mainloop()
