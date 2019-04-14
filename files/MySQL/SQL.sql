create table drivers
(
    id           int          not null,
    forename     varchar(30)  not null,
    name         varchar(30)  not null,
    `e-mail`     varchar(30)  not null,
    password     varchar(128) not null,
    tel          varchar(30)  null,
    seats        int          not null,
    street       varchar(50)  not null,
    streetNumber int          null,
    locality     varchar(50)  not null,
    region       varchar(50)  not null,
    zipcode      varchar(50)  not null,
    country      varchar(50)  not null,
    constraint id
        unique (id)
);

alter table drivers
    add primary key (id);


create table passengers
(
    id           int          not null,
    forename     varchar(30)  null,
    name         varchar(30)  null,
    `e-mail`     varchar(30)  null,
    password     varchar(128) null,
    tel          varchar(30)  null,
    street       varchar(50)  null,
    streetNumber int          null,
    locality     varchar(50)  null,
    region       varchar(50)  null,
    zipcode      varchar(50)  null,
    country      varchar(50)  null,
    constraint id
        unique (id)
);

alter table passengers
    add primary key (id);


create table users
(
    id        int auto_increment
        primary key,
    monday    time       null,
    tuesday   time       null,
    wednesday time       null,
    thursday  time       null,
    friday    time       null,
    school_id int        null,
    status    tinyint(1) not null,
    constraint school_id
        foreign key (school_id) references schools (id)
            on update cascade on delete cascade
);


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
