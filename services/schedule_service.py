from database import (
    add_section_schedule,
    check_schedule_conflict,
    delete_schedule,
    delete_section_schedule,
    get_program_schedule,
    get_schedule_occurrences,
    get_section_by_name,
    get_section_schedules,
    get_user_schedules,
    update_program_schedule,
    update_schedule,
    update_section_schedule,
)


class ScheduleService:
    def get_program_schedule(self, program_type):
        return get_program_schedule(program_type)

    def update_program_schedule(self, schedule_id, time_range, subject, teacher):
        return update_program_schedule(schedule_id, time_range, subject, teacher)

    def get_section_schedules(self, section_id):
        return get_section_schedules(section_id)

    def add_section_schedule(self, section_id, time_range, subject, teacher=""):
        return add_section_schedule(section_id, time_range, subject, teacher)

    def update_section_schedule(self, schedule_id, time_range, subject, teacher):
        return update_section_schedule(schedule_id, time_range, subject, teacher)

    def delete_section_schedule(self, schedule_id):
        return delete_section_schedule(schedule_id)

    def get_student_timetable(self, user):
        program_type = user.get("program_type") or "Regular"
        if program_type == "N/A":
            program_type = "Regular"

        section_name = user.get("section") or ""
        schedules = []
        schedule_label = f"{program_type} Program"

        if section_name:
            section = get_section_by_name(section_name)
            if section:
                schedules = get_section_schedules(section["id"])
                schedule_label = f"Section: {section_name}"

        if not schedules:
            schedules = get_program_schedule(program_type)
            schedule_label = f"{program_type} Program (Template)"

        return {
            "program_type": program_type,
            "schedule_label": schedule_label,
            "schedules": schedules,
        }

    def get_user_schedules(self, user_id):
        return get_user_schedules(user_id)

    def get_schedule_occurrences(self, user_id, window_start, window_end):
        return get_schedule_occurrences(user_id, window_start, window_end)

    def check_schedule_conflict(self, user_id, start_dt, end_dt, **kwargs):
        return check_schedule_conflict(user_id, start_dt, end_dt, **kwargs)

    def update_schedule(self, schedule_id, title, start_dt, end_dt, **kwargs):
        return update_schedule(schedule_id, title, start_dt, end_dt, **kwargs)

    def delete_schedule(self, schedule_id):
        return delete_schedule(schedule_id)
