set names utf8;
set character_set_results=gbk;

drop database if exists appstore;
create database appstore character set utf8 collate utf8_general_ci;
use appstore;

drop table if exists iosapp;
create table iosapp(
		ID char(9) not null,
		name text,
		seller text,
		price varchar(255),
		category varchar(255) default null,
		updated date default null,
		version varchar(100) default null,
		size decimal(5,1) default null,
		language text,
		seller_spec text,
		copy_right text,
		limit_grade varchar(255) default null,
		compatibility text,
		rating_all decimal(2,1) default null,
		ra_amount int default null,
		rating_current decimal(2,1) default null,
		rc_amount int default null,
		in_app_purchase text,
		more_app text,
		comment_1 text,
		rate_1 decimal(2,1) default null,
		comment_2 text,
		rate_2 decimal(2,1) default null,
		comment_3 text,
		rate_3 decimal(2,1) default null,
		purchase_also_1 text,
		purchase_also_2 text,
		purchase_also_3 text,
		purchase_also_4 text,
		purchase_also_5 text,
		content text,
		primary key (ID)
	)ENGINE=InnoDB default charset=utf8;