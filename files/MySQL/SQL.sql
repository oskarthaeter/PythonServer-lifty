create table schools
(
    id           int         not null
        primary key,
    name         varchar(50) null,
    street       varchar(50) null,
    streetNumber int         null,
    locality     varchar(50) null,
    region       varchar(50) null,
    zipcode      varchar(50) null,
    country      varchar(50) null,
    timezone     int         not null
);

create table timetable
(
    id        int auto_increment
        primary key,
    monday    time       null,
    tuesday   time       null,
    wednesday time       null,
    thursday  time       null,
    friday    time       null,
    status    tinyint(1) not null
);

create table users
(
    id           int          not null,
    forename     varchar(30)  not null,
    name         varchar(30)  not null,
    `e-mail`     varchar(30)  not null,
    password     varchar(128) not null,
    tel          varchar(30)  null,
    seats        int          null,
    street       varchar(50)  not null,
    streetNumber int          null,
    locality     varchar(50)  not null,
    region       varchar(50)  not null,
    zipcode      varchar(50)  not null,
    country      varchar(50)  not null,
    school_id    int          not null,
    constraint id
        unique (id),
    constraint users_schools_id_fk
        foreign key (school_id) references schools (id)
            on update cascade on delete cascade
);

alter table users
    add primary key (id);
