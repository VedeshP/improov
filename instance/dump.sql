BEGIN TRANSACTION;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    display_name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    email_id TEXT NOT NULL UNIQUE
);
INSERT INTO users (username, password, display_name, date_of_birth, email_id) VALUES('vedeshp','scrypt:32768:8:1$QBXrX0DmCiZkOWdX$ace7f24f42bbae6a39b735afa01653883ad618bea9d083eae84d58f0f384fc5fe17eaeb484a0f1663d35e07cb80496ddd68591ece1bfcfad83079e856b3b73ed','Vedesh P','2005-04-04','vedeshskp@gmail.com');
INSERT INTO users (username, password, display_name, date_of_birth, email_id) VALUES('improovapp','scrypt:32768:8:1$2iHf6K0tEiih3YMe$8ec193c9f5fc6058b06c0e8a67700f4b08d6a2607743cbb8efb964bcff6cb9de17138f2ee83b348a7319457e376b200c21a6d18541820090c6116027fa9042a6','Improov','2005-04-04','improovbyvp@gmail.com');
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    main_topic TEXT,
    sub_topic TEXT,
    link TEXT,
    likes INTEGER DEFAULT 0, created_at TIMESTAMP, iframe TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(1,'This is my first post on Improov, I created this app!','1','1',NULL,2,'2024-06-04 18:40:43.020750',NULL);
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(1,'This is my first official post on Improov, let us be mindful of our usage of technology','Mind','None',NULL,3,'2024-06-04 18:44:27.791435',NULL);
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(1,'One of the best Ted Talks I''ve watched, Sir Ken Robinson points that our efforts in education are applied in the wrong direction','Mind','None','https://youtu.be/wX78iKhInsc?si=_8ZJjndtnxEJr3x5',2,'2024-06-05 16:14:44.500715','<iframe width="200" height="113" src="https://www.youtube.com/embed/wX78iKhInsc?feature=oembed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen title="How to escape education&#39;s death valley | Sir Ken Robinson | TED"></iframe>');
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(1,'Why do I exist ? Have you ever got this question in your mind ?','Mind','None','https://youtu.be/zORUUqJd81M?si=YXf13VfBElFU2hO8',1,'2024-06-06 03:53:26.108169','<iframe width="200" height="113" src="https://www.youtube.com/embed/zORUUqJd81M?feature=oembed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen title="Why does the universe exist? | Jim Holt | TED"></iframe>');
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(1,'Health, Happiness and Love                                                                      That''s all we yearn for','Mind','None','https://youtu.be/pgmiPXAwiLg?si=6o5sEmbmHbat3HHz',2,'2024-06-06 05:11:22.142286','<iframe width="200" height="113" src="https://www.youtube.com/embed/pgmiPXAwiLg?feature=oembed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen title="My failed mission to find God -- and what I found instead | Anjali Kumar"></iframe>');
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(1,'A really good quality video by Mark Manson','Mind','None','https://youtu.be/lwmVAWXQyY4?si=HtMxZMRQAiBhIvCH',3,'2024-06-06 06:33:32.467295','<iframe width="200" height="113" src="https://www.youtube.com/embed/lwmVAWXQyY4?feature=oembed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen title="40 Harsh Truths I Know at 40 but Wish I Knew at 20"></iframe>');
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(2,'Welcome to Improov! Bring the CHANGE, be the CHANGE','Mind','None',NULL,2,'2024-06-07 12:28:04.456188',NULL);
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(1,'How we take care of our mental health is an important factor in determining the quality of our life','Mind','Mental Health',NULL,1,'2024-06-09 05:12:09.786665',NULL);
INSERT INTO posts (user_id, content, main_topic, sub_topic, link, likes, created_at, iframe) VALUES(1,'Sleep is indeed our superpower Best type of active recovery method ','Body','Physical Health','https://youtu.be/5MuIMqhT8DM?si=uS_y9HuKdVlSiaLX',0,'2024-06-10 09:52:19.884287','<iframe width="200" height="113" src="https://www.youtube.com/embed/5MuIMqhT8DM?feature=oembed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen title="Sleep Is Your Superpower | Matt Walker | TED"></iframe>');
CREATE TABLE likes (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);
INSERT INTO likes (user_id, post_id) VALUES(1,3);
INSERT INTO likes (user_id, post_id) VALUES(1,2);
INSERT INTO likes (user_id, post_id) VALUES(1,5);
INSERT INTO likes (user_id, post_id) VALUES(1,6);
INSERT INTO likes (user_id, post_id) VALUES(2,4);
INSERT INTO likes (user_id, post_id) VALUES(2,3);
INSERT INTO likes (user_id, post_id) VALUES(2,1);
INSERT INTO likes (user_id, post_id) VALUES(2,6);
INSERT INTO likes (user_id, post_id) VALUES(1,7);
INSERT INTO likes (user_id, post_id) VALUES(2,7);
INSERT INTO likes (user_id, post_id) VALUES(2,2);
INSERT INTO likes (user_id, post_id) VALUES(1,8);
INSERT INTO likes (user_id, post_id) VALUES(1,1);
CREATE TABLE bookmarks (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);
INSERT INTO bookmarks (user_id, post_id) VALUES(1,3);
INSERT INTO bookmarks (user_id, post_id) VALUES(1,2);
INSERT INTO bookmarks (user_id, post_id) VALUES(1,4);
INSERT INTO bookmarks (user_id, post_id) VALUES(1,6);
INSERT INTO bookmarks (user_id, post_id) VALUES(2,5);
INSERT INTO bookmarks (user_id, post_id) VALUES(2,4);
INSERT INTO bookmarks (user_id, post_id) VALUES(1,7);
CREATE TABLE follows (
    user_id INTEGER NOT NULL,
    following_user_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, following_user_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (following_user_id) REFERENCES users(id)
);
INSERT INTO follows (user_id, following_user_id) VALUES(2,1);
INSERT INTO follows (user_id, following_user_id) VALUES(2,2);
INSERT INTO follows (user_id, following_user_id) VALUES(1,2);
CREATE TABLE replies (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reply TEXT NOT NULL, created_on TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
INSERT INTO replies (post_id, user_id, reply, created_on) VALUES(7,1,'Together WE will!','2024-06-08 06:05:27.185778');
INSERT INTO replies (post_id, user_id, reply, created_on) VALUES(4,2,'I got that question, still','2024-06-08 13:07:47.705980');
INSERT INTO replies (post_id, user_id, reply, created_on) VALUES(4,2,'I was really searching the answer to this question. Thank you!','2024-06-08 13:18:17.838565');
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    sub_topic TEXT NOT NULL UNIQUE,
    main_topic TEXT NOT NULL
);
INSERT INTO topics (sub_topic, main_topic) VALUES('Mental Health','Mind');
INSERT INTO topics (sub_topic, main_topic) VALUES('Education','Mind');
INSERT INTO topics (sub_topic, main_topic) VALUES('Philosophy','Mind');
INSERT INTO topics (sub_topic, main_topic) VALUES('Physical Health','Body');
INSERT INTO topics (sub_topic, main_topic) VALUES('Physical Fitness','Body');
INSERT INTO topics (sub_topic, main_topic) VALUES('Relationships','Soul');
INSERT INTO topics (sub_topic, main_topic) VALUES('Profession','Soul');
INSERT INTO topics (sub_topic, main_topic) VALUES('Spirituality & Self-Discovery','Soul');
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users), true);
SELECT setval('posts_id_seq', (SELECT MAX(id) FROM posts), true);
SELECT setval('replies_id_seq', (SELECT MAX(id) FROM replies), true);
SELECT setval('topics_id_seq', (SELECT MAX(id) FROM topics), true);
COMMIT;
