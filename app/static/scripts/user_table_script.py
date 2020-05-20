import csv
from faker import Faker


def datagenerate(records, headers):
    fake = Faker()
    with open("./csv files/user_data_fake.csv", 'wt') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader()
        for i in range(records):
            f_name = fake.first_name()
            l_name = fake.last_name()
            username = f_name
            email = l_name + "@gmail.com"
            password = "mybook2020"

            writer.writerow({
                "User Id": i+1,
                "First Name": f_name,
                "Last Name": l_name,
                "Username": f_name,
                "Email": email,
                "Password": password,
            })


# How to write CSV to Database
# Run this command in mysql

# LOAD DATA LOCAL INFILE 'C:/Users/Loretta/Desktop/MyBook/app/static/scripts/CSV Files/user_data.csv' INTO TABLE user FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\r' IGNORE 1 ROWS(user_id, f_name, l_name, username, @password, email) SET password = HEX(AES_ENCRYPT(@password, 'key'));


if __name__ == '__main__':
    records = 5
    headers = ["User Id", "First Name", "Last Name",
               "Username", "Password", "Email"]
    datagenerate(records, headers)
    print("User Table CSV generation complete!")
