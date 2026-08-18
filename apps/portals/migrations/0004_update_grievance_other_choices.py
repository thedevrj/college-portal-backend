from django.db import migrations, models


def forwards(apps, schema_editor):
    Grievance = apps.get_model("portals", "Grievance")
    HistoricalGrievance = apps.get_model("portals", "HistoricalGrievance")

    Grievance.objects.filter(nature_of_grievance="Other").update(
        nature_of_grievance="other"
    )
    Grievance.objects.filter(complainant_type="Other").update(
        complainant_type="other"
    )

    HistoricalGrievance.objects.filter(nature_of_grievance="Other").update(
        nature_of_grievance="other"
    )
    HistoricalGrievance.objects.filter(complainant_type="Other").update(
        complainant_type="other"
    )


def backwards(apps, schema_editor):
    Grievance = apps.get_model("portals", "Grievance")
    HistoricalGrievance = apps.get_model("portals", "HistoricalGrievance")

    Grievance.objects.filter(nature_of_grievance="other").update(
        nature_of_grievance="Other"
    )
    Grievance.objects.filter(complainant_type="other").update(
        complainant_type="Other"
    )

    HistoricalGrievance.objects.filter(nature_of_grievance="other").update(
        nature_of_grievance="Other"
    )
    HistoricalGrievance.objects.filter(complainant_type="other").update(
        complainant_type="Other"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("portals", "0003_alter_grievance_complainant_type_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.AlterField(
            model_name="grievance",
            name="nature_of_grievance",
            field=models.CharField(
                choices=[
                    ("admission_contrary_to_merit", "Making admission contrary to merit"),
                    ("irregularity_in_admission", "Irregularity in the admission process"),
                    (
                        "refusing_admission",
                        "Refusing admission in accordance with the declared admission policy of the institute",
                    ),
                    ("non_publication_of_prospectus", "Non publication of prospectus"),
                    (
                        "false_misleading_prospectus",
                        "Publishing false or misleading information in the prospectus",
                    ),
                    (
                        "withhold_documents",
                        "Withhold or refuse to return any document (certificates/degree/diploma or any other award/document for the purpose of seeking admission)",
                    ),
                    (
                        "excess_fee_demand",
                        "Demand of money in excess of that specified in the declared admission policy",
                    ),
                    (
                        "reservation_policy_breach",
                        "Breach of the policy for reservation in admission",
                    ),
                    (
                        "discrimination",
                        "Complaints of alleged discrimination of students from SC/ST/OBC/Women/Minority or Disabled categories",
                    ),
                    (
                        "scholarship_delay",
                        "Non payment or delay in payment of scholarships to any student",
                    ),
                    ("exam_delay", "Delay in conduct of examinations or declaration of results"),
                    ("no_student_amenities", "No provision of student amenities"),
                    ("unfair_evaluation", "Unfair evaluation practices"),
                    ("other", "Others"),
                ],
                max_length=100,
                verbose_name="Nature of Grievance",
            ),
        ),
        migrations.AlterField(
            model_name="grievance",
            name="other_nature_of_grievance",
            field=models.CharField(
                blank=True,
                help_text="Required if Nature of Grievance is 'Others'",
                max_length=255,
                null=True,
                verbose_name="Specify Other Nature of Grievance",
            ),
        ),
        migrations.AlterField(
            model_name="grievance",
            name="complainant_type",
            field=models.CharField(
                choices=[
                    ("student", "Student"),
                    ("faculty", "Faculty"),
                    ("non_teaching_staff", "Non Teaching Staff"),
                    ("other", "Others"),
                ],
                max_length=50,
                verbose_name="Complainant",
            ),
        ),
        migrations.AlterField(
            model_name="grievance",
            name="other_complainant_type",
            field=models.CharField(
                blank=True,
                help_text="Required if Complainant Type is 'Others'",
                max_length=255,
                null=True,
                verbose_name="Specify Other Complainant Type",
            ),
        ),
        migrations.AlterField(
            model_name="historicalgrievance",
            name="nature_of_grievance",
            field=models.CharField(
                choices=[
                    ("admission_contrary_to_merit", "Making admission contrary to merit"),
                    ("irregularity_in_admission", "Irregularity in the admission process"),
                    (
                        "refusing_admission",
                        "Refusing admission in accordance with the declared admission policy of the institute",
                    ),
                    ("non_publication_of_prospectus", "Non publication of prospectus"),
                    (
                        "false_misleading_prospectus",
                        "Publishing false or misleading information in the prospectus",
                    ),
                    (
                        "withhold_documents",
                        "Withhold or refuse to return any document (certificates/degree/diploma or any other award/document for the purpose of seeking admission)",
                    ),
                    (
                        "excess_fee_demand",
                        "Demand of money in excess of that specified in the declared admission policy",
                    ),
                    (
                        "reservation_policy_breach",
                        "Breach of the policy for reservation in admission",
                    ),
                    (
                        "discrimination",
                        "Complaints of alleged discrimination of students from SC/ST/OBC/Women/Minority or Disabled categories",
                    ),
                    (
                        "scholarship_delay",
                        "Non payment or delay in payment of scholarships to any student",
                    ),
                    ("exam_delay", "Delay in conduct of examinations or declaration of results"),
                    ("no_student_amenities", "No provision of student amenities"),
                    ("unfair_evaluation", "Unfair evaluation practices"),
                    ("other", "Others"),
                ],
                max_length=100,
                verbose_name="Nature of Grievance",
            ),
        ),
        migrations.AlterField(
            model_name="historicalgrievance",
            name="other_nature_of_grievance",
            field=models.CharField(
                blank=True,
                help_text="Required if Nature of Grievance is 'Others'",
                max_length=255,
                null=True,
                verbose_name="Specify Other Nature of Grievance",
            ),
        ),
        migrations.AlterField(
            model_name="historicalgrievance",
            name="complainant_type",
            field=models.CharField(
                choices=[
                    ("student", "Student"),
                    ("faculty", "Faculty"),
                    ("non_teaching_staff", "Non Teaching Staff"),
                    ("other", "Others"),
                ],
                max_length=50,
                verbose_name="Complainant",
            ),
        ),
        migrations.AlterField(
            model_name="historicalgrievance",
            name="other_complainant_type",
            field=models.CharField(
                blank=True,
                help_text="Required if Complainant Type is 'Others'",
                max_length=255,
                null=True,
                verbose_name="Specify Other Complainant Type",
            ),
        ),
    ]
