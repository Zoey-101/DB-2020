import csv
from faker import Faker


def datagenerate(records, headers):
    fake = Faker()
    with open("./csv files/group_data_fake.csv", 'wt') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader()
        for i in range(records):
            g_name = fake.company()
            g_purpose = fake.catch_phrase()

            writer.writerow({
                "Group Id": i+1,
                "Group Name": fake.profile(fields=['name'])['name'] + 'Group',
                "Purpose": "Our Life",
            })


# How to write CSV to Database
# Run this command in mysql
# LOAD DATA LOCAL INFILE 'C:/Users/Loretta/Desktop/MyBook/app/static/scripts/CSV Files/group_data_fake.csv' INTO TABLE grouped FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 ROWS (grp_id, grp_name, purpose);


if __name__ == '__main__':
    records = 8
    headers = ["Group Id", "Group Name", "Purpose"]
    datagenerate(records, headers)
    print("Groups CSV generation complete!")
