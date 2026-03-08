from database import get_student_grades, initialize_grades, save_grades_batch


class GradeService:
    def get_student_grades(self, user_id, initialize_if_missing=False):
        grades = get_student_grades(user_id)
        if initialize_if_missing and not grades:
            initialize_grades(user_id)
            grades = get_student_grades(user_id)
        return grades

    def calculate_general_average(self, grades):
        final_values = [grade["final"] for grade in grades if grade.get("final") is not None]
        if not final_values:
            return None
        return round(sum(final_values) / len(final_values))

    def build_grade_updates(self, raw_updates):
        updates = []
        computed_finals = {}
        final_grades = []

        for grade_id, row in raw_updates.items():
            row_data = {}
            quarter_values = []

            for field in ["q1", "q2", "q3", "q4"]:
                value = (row.get(field) or "").strip()
                if value:
                    if not value.isdigit():
                        return {
                            "success": False,
                            "message": f"Grades must be numbers. Check row with ID {grade_id}.",
                        }
                    numeric_value = int(value)
                    if not 0 <= numeric_value <= 100:
                        return {
                            "success": False,
                            "message": f"Grades must be between 0 and 100. Check row with ID {grade_id}.",
                        }
                    row_data[field] = numeric_value
                    quarter_values.append(numeric_value)
                else:
                    row_data[field] = None

            if quarter_values:
                computed_final = round(sum(quarter_values) / len(quarter_values))
                row_data["final"] = computed_final
                computed_finals[grade_id] = computed_final
                final_grades.append(computed_final)
            else:
                row_data["final"] = None
                computed_finals[grade_id] = None

            row_data["remarks"] = (row.get("remarks") or "").strip()
            updates.append((grade_id, row_data))

        general_average = None
        if final_grades:
            general_average = sum(final_grades) / len(final_grades)

        return {
            "success": True,
            "updates": updates,
            "computed_finals": computed_finals,
            "general_average": general_average,
        }

    def save_grade_updates(self, raw_updates):
        prepared = self.build_grade_updates(raw_updates)
        if not prepared["success"]:
            return prepared

        success, error_message = save_grades_batch(prepared["updates"])
        if not success:
            return {
                "success": False,
                "message": f"Database error: {error_message}",
            }

        prepared["message"] = "All grades have been saved successfully!"
        return prepared
