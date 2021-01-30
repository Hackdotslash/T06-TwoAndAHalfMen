CREATE TABLE USER (id integer primary key autoincrement, name text, phone_no text);

CREATE TABLE doctor (id integer primary key autoincrement, name text, phone_no text, email text unique, registration_no integer not null, medical_council text not null, latitude decimal(10,8), longitude decimal(11,8), password text);

create table conference(zoom_id integer primary key not null, start_timestamp timestamp, end_timestamp timestamp, title text, host_doctor_id integer, foreign key (host_doctor_id) references doctor(id));

create table blogpost(title text not null, author_id primary key not null, published_at timestamp, body text not null);

-- dummy data insertion

insert into user values(NULL, "Kaustubh Damania", "1234567890");

insert into user values(NULL, "Gaurav Bhagwanani", "2345678901");


insert into doctor values("Deep Dama", "3456789012", "deep.dama@gmail.com" ,"1234567890", "Maharashtra", 19.116884428986182, 72.93164483021962, "abcdef");

insert into doctor values("KD", "3456789012", "kaustubh.damania@gmail.com" ,"1234567890", "Maharashtra", 19.10123794041552, 72.91207824204169, "abcdef");
