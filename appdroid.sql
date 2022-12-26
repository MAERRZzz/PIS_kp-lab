-- MySQL dump 10.13  Distrib 8.0.30, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: appdroid
-- ------------------------------------------------------
-- Server version	8.0.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `color`
--

DROP TABLE IF EXISTS `color`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `color` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `color`
--

LOCK TABLES `color` WRITE;
/*!40000 ALTER TABLE `color` DISABLE KEYS */;
INSERT INTO `color` VALUES (1,'Золотистый'),(2,'Золотой'),(3,'Серебристый'),(4,'Фиолетовый'),(5,'Черный'),(7,'Лавандовый'),(8,'Перламутровый'),(9,'СЕРЕБРИСТО-белый');
/*!40000 ALTER TABLE `color` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `active` tinyint NOT NULL,
  PRIMARY KEY (`id`,`user_id`),
  KEY `fk_order_user1_idx` (`user_id`),
  CONSTRAINT `fk_order_user1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
INSERT INTO `order` VALUES (30,1,1);
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_has_phone`
--

DROP TABLE IF EXISTS `order_has_phone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_has_phone` (
  `order_id` int NOT NULL,
  `phone_id` int NOT NULL,
  `phone_color` varchar(45) NOT NULL,
  `count` varchar(45) NOT NULL,
  `add_date` datetime NOT NULL,
  KEY `fk_order_has_phone_order1_idx` (`order_id`),
  KEY `fk_order_has_phone_phone1_idx` (`phone_color`),
  KEY `fk_order_has_phone_phone1_idx1` (`phone_id`),
  CONSTRAINT `fk_order_has_phone_order1` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_order_has_phone_phone1` FOREIGN KEY (`phone_id`) REFERENCES `phone` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_has_phone`
--

LOCK TABLES `order_has_phone` WRITE;
/*!40000 ALTER TABLE `order_has_phone` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_has_phone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `method` varchar(45) NOT NULL,
  `date` datetime NOT NULL,
  `courier` varchar(5) NOT NULL,
  `order_id1` int NOT NULL,
  `order_user_id` int NOT NULL,
  PRIMARY KEY (`id`,`order_id`,`order_id1`,`order_user_id`),
  KEY `fk_payment_order1_idx` (`order_id`),
  KEY `fk_payment_order1_idx1` (`order_id1`,`order_user_id`),
  CONSTRAINT `fk_payment_order1` FOREIGN KEY (`order_id1`, `order_user_id`) REFERENCES `order` (`id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phone`
--

DROP TABLE IF EXISTS `phone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `phone` (
  `id` int NOT NULL AUTO_INCREMENT,
  `brand` varchar(45) NOT NULL,
  `model` varchar(100) NOT NULL,
  `OS` varchar(45) NOT NULL,
  `year` year NOT NULL,
  `price` int NOT NULL,
  `diagonal` decimal(4,2) NOT NULL,
  `NFC` varchar(5) NOT NULL,
  `RAM` int NOT NULL,
  `memory` int NOT NULL,
  `SIM` int NOT NULL,
  `cores` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phone`
--

LOCK TABLES `phone` WRITE;
/*!40000 ALTER TABLE `phone` DISABLE KEYS */;
INSERT INTO `phone` VALUES (1,'Samsung','Galaxy J7','Android',2016,1000000,5.50,'Есть',2,16,2,8),(2,'Apple','iPhone 14 Pro','IOS',2022,119999,6.10,'Есть',6,256,2,6),(3,'Samsung','Galaxy A23','Android',2022,19499,6.60,'Есть',6,128,2,8),(4,'Samsung','Galaxy Z Flip4','Android',2022,64999,6.70,'Есть',8,128,2,8),(6,'Realme','GT Master Edition','Android',2021,29999,6.43,'Есть',6,128,2,8),(7,'Xiaomi','Redmi 8','Android',2019,1000000,6.22,'Нет',4,64,2,8);
/*!40000 ALTER TABLE `phone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phone_has_color`
--

DROP TABLE IF EXISTS `phone_has_color`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `phone_has_color` (
  `phone_id` int NOT NULL,
  `color_id` int NOT NULL,
  `count` varchar(45) NOT NULL,
  `image` varchar(200) NOT NULL,
  PRIMARY KEY (`phone_id`,`color_id`),
  KEY `fk_phone_has_color_phone1_idx` (`phone_id`),
  KEY `fk_phone_has_color_phone2_idx` (`color_id`),
  CONSTRAINT `color_id` FOREIGN KEY (`color_id`) REFERENCES `color` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `phone_id` FOREIGN KEY (`phone_id`) REFERENCES `phone` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phone_has_color`
--

LOCK TABLES `phone_has_color` WRITE;
/*!40000 ALTER TABLE `phone_has_color` DISABLE KEYS */;
INSERT INTO `phone_has_color` VALUES (1,1,'1','https://cdn.svyaznoy.ru/upload/iblock/3bd/3366125_12.jpg/resize/870x725/hq/'),(2,2,'4','https://cdn.svyaznoy.ru/upload/iblock/f70/f70e29594da332ec0a6313b52801c426.jpg/resize/870x725/hq/'),(2,3,'7','https://cdn.svyaznoy.ru/upload/iblock/f98/f982b8c8e7f6a1d151088cf0856f8361.jpg/resize/870x725/hq/'),(2,4,'3','https://c.dns-shop.ru/thumb/st4/fit/0/0/dadce80b9f35b6b4d5200f4327cc37f0/3012baa9bc23995289e498d33793b6007a246987cd6e5bd96dbd15aa6cd93c2c.jpg.webp'),(3,5,'5','https://c.dns-shop.ru/thumb/st4/fit/0/0/7554657016ea5bd8b523f9c92d5365ca/956357c5641a2dba5283d04496d49e314353a193bf8d7515af21ab83cd43913f.jpg.webp'),(4,7,'2','https://c.dns-shop.ru/thumb/st1/fit/0/0/cd4fc0520c20f51690b5250b3b7478fb/ace0209987f9b7355310041a40b081212bd05312fa142e7cf29f7537e9caba71.jpg.webp'),(6,8,'7','https://c.dns-shop.ru/thumb/st4/fit/0/0/26acc16ac790fe537be5a6d7c7e83eb5/acc5427d5d0f773730351e60868497738352302b986151bc590ca07d861d8e3a.jpg.webp'),(7,5,'1','https://mi-shop.com/upload/iblock/33e/33e277e6d6cfe740ecbed29a01b7e7c3.jpg');
/*!40000 ALTER TABLE `phone_has_color` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `nickname` varchar(45) NOT NULL,
  `password` varchar(150) NOT NULL,
  `admin` tinyint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Эрнест','Мамутов','MAERZ','$5$rounds=535000$zm/qx7jt/bn7NUkJ$jShJtivWrsctUoJupM/VxK4h1UgN9sy/ur5eogmnFF3',1),(2,'Казим','Казимов','kazim','$5$rounds=535000$VFSZ5wmtMP0ryqq1$4TtN3LH7cfIXJ97MNZ53htWsXbUGH8DK6iNTSdJdQu6',0),(3,'Эмиль','Мамутов','MAEMJ','$5$rounds=535000$1843SAVYnysZrGys$btg/PBm4Ip2V/xob.5G2V1mvShq3MMJH68xLmBsL1Y.',0),(4,'Джон','Хуиблон','JHONIDZE','$5$rounds=535000$rcyawryxCuHXHQzM$07sUCz9CseCHO06eZIS6q8qjDbeHMi5iy.00/ak11h1',0),(5,'Тест','Тестов','test','$5$rounds=535000$3uxFjvwOLtZnf219$18AHIMXvH1/gdvmK5KXP4ltRRbu6v4rGKAk2yfxRjm9',0);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-27  1:17:01
