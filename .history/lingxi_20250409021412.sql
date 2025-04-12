create table auth_user
(
    id           int auto_increment
        primary key,
    username     varchar(30)          not null,
    password     varchar(128)         not null,
    phone_number varchar(15)          not null,
    email        varchar(255)         null,
    bio          text                 null,
    avatar       varchar(255)         null,
    is_active    tinyint(1) default 1 not null,
    is_admin     tinyint(1) default 0 not null,
    created_at   datetime            not null default CURRENT_TIMESTAMP,
    updated_at   datetime            not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
    last_login   datetime            null,
    ban_reason   text                null,
    ban_until    datetime            null,
    constraint phone_number
        unique (phone_number),
    constraint username
        unique (username)
);

-- 创建智能体表
-- 该表用于存储智能体的相关信息
CREATE TABLE agent (
    -- 智能体的唯一标识，自增长，作为表的主键
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- 智能体的名称，不能为空，用于区分不同的智能体
    agent_name VARCHAR(255) NOT NULL,
    -- 创建智能体的用户的ID，与auth_user表中的id关联，用于标识智能体的创建者
    creator_id INT NOT NULL,
    -- 外键约束，关联auth_user表的id字段，确保creator_id的值在auth_user表中存在
    FOREIGN KEY (creator_id) REFERENCES auth_user(id)
);

-- 创建智能体评价表
-- 该表用于存储对智能体的评价信息
CREATE TABLE agent_evaluation (
    -- 评价的唯一标识，自增长，作为表的主键
    evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    -- 被评价的智能体的ID，与agent表中的id关联，用于确定评价针对的智能体
    agent_id INT NOT NULL,
    -- 评价者的用户ID，与auth_user表中的id关联，用于标识评价的发起者
    evaluator_id INT NOT NULL,
    -- 评价的具体内容，使用TEXT类型可以存储较长的文本内容
    evaluation_content TEXT NOT NULL,
    -- 外键约束，关联agent表的id字段，确保agent_id的值在agent表中存在
    FOREIGN KEY (agent_id) REFERENCES agent(id),
    -- 外键约束，关联auth_user表的id字段，确保evaluator_id的值在auth_user表中存在
    FOREIGN KEY (evaluator_id) REFERENCES auth_user(id)
);

-- 创建关注表
-- 该表用于存储用户之间的关注关系
CREATE TABLE follow (
    -- 关注关系的唯一标识，自增长，作为表的主键
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- 关注他人的用户的ID，与auth_user表中的id关联，用于标识关注者
    follower_id INT NOT NULL,
    -- 被关注的用户的ID，与auth_user表中的id关联，用于标识被关注者
    followed_id INT NOT NULL,
    -- 外键约束，关联auth_user表的id字段，确保follower_id的值在auth_user表中存在
    FOREIGN KEY (follower_id) REFERENCES auth_user(id),
    -- 外键约束，关联auth_user表的id字段，确保followed_id的值在auth_user表中存在
    FOREIGN KEY (followed_id) REFERENCES auth_user(id)
);


