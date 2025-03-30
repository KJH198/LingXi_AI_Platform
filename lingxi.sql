create table auth_user
(
    id           int auto_increment
        primary key,
    username     varchar(30)          not null,
    password     varchar(128)         not null,
    phone_number varchar(15)          not null,
    email        varchar(255)         null,
    is_active    tinyint(1) default 1 not null,
    is_admin     tinyint(1) default 0 not null,
    constraint phone_number
        unique (phone_number),
    constraint username
        unique (username)
);


