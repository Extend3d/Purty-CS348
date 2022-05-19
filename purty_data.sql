--
-- Table structure for table `User`
--

CREATE TABLE User (
  user_id INTEGER PRIMARY KEY NOT NULL,
  name NVARCHAR(40) NOT NULL,
  email NVARCHAR(100) NOT NULL,
  age INTEGER NOT NULL
);

CREATE UNIQUE INDEX idx_email
ON User (email);

--
-- Dumping data for table `User`
--

INSERT INTO User (user_id, name, email, age) VALUES
('1', 'Arda Gurer', 'agurer@purdue.edu', 23),
('2', 'Mike Fisher', 'mfisher@purdue.edu', 22),
('3', 'John Smith', 'jsmith@purdue.edu', 24),
('4', 'David Cameron', 'dcameron@purdue.edu', 53),
('5', 'Ron Paul', 'rpaul@purdue.edu', 72),
('6', 'Max Long', 'mlong@purdue.edu', 18);

-- --------------------------------------------------------

--
-- Table structure for table `Host`
--

CREATE TABLE Host (
  host_id INTEGER PRIMARY KEY NOT NULL,
  party_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL
);

--
-- Dumping data for table `Host`
--

INSERT INTO Host (host_id, party_id, user_id) VALUES
('1', '1', '2');


-- --------------------------------------------------------

--
-- Table structure for table `Party`
--

CREATE TABLE Party (
  party_id INTEGER PRIMARY KEY NOT NULL,
  name NVARCHAR(40) NOT NULL,
  date NVARCHAR(40) NOT NULL,
  time NVARCHAR(40) NOT NULL,
  description NVARCHAR(400) NOT NULL,
  location_id INTEGER NOT NULL,
  invited_cnt INTEGER NOT NULL,
  coming_cnt INTEGER NOT NULL,
  likes_cnt INTEGER NOT NULL
);

--
-- Dumping data for table `Party`
--

INSERT INTO Party (party_id, name, date, time, description, location_id, invited_cnt, coming_cnt, likes_cnt) VALUES
('1', 'House Party!', '04/12/2021', '20:00', 'house party 101', '1', 2, 2, 2);


-- --------------------------------------------------------

--
-- Table structure for table `Location`
--

CREATE TABLE Location (
  location_id INTEGER PRIMARY KEY NOT NULL,
  address NVARCHAR(400) NOT NULL
);

--
-- Dumping data for table `Location`
--

INSERT INTO Location (location_id, address) VALUES
('1', '111 South Salisbury Street');


-- --------------------------------------------------------

--
-- Table structure for table `Invites`
--

CREATE TABLE Invites (
  party_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  invitation_date NVARCHAR(40) NOT NULL,
  reply_date NVARCHAR(40),
  answer INTEGER,
  PRIMARY KEY (party_id, user_id)
);

CREATE INDEX idx_replyDate_inv
on Invites(reply_date);

--
-- Dumping data for table `Invites`
--

INSERT INTO Invites (party_id, user_id, invitation_date, reply_date, answer) VALUES
(1, 4, '04/12/2021', '04/12/2021', 1),
(1, 5, '04/12/2021', '04/12/2021', 0),
(1, 6, '04/12/2021', NULL, NULL);


-- --------------------------------------------------------

--
-- Table structure for table `Requests`
--

CREATE TABLE Requests (
  party_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  request_date NVARCHAR(40) NOT NULL,
  reply_date NVARCHAR(40),
  answer INTEGER,
  PRIMARY KEY (party_id, user_id)
);

CREATE INDEX idx_replyDate_req
ON Requests(reply_date);

--
-- Dumping data for table `Requests`
--

 INSERT INTO `Requests` (`party_id`, `user_id`, `request_date`, `reply_date`, `answer`) VALUES
 (1, 1, '04/12/2021', '04/12/2021', 1),
 (1, 2, '04/12/2021', '04/12/2021', 0),
 (1, 3, '04/12/2021', NULL, NULL);


-- --------------------------------------------------------

--
-- Table structure for table `Likes`
--

CREATE TABLE Likes (
  party_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  like_status INTEGER NOT NULL,
  PRIMARY KEY (party_id, user_id)
);

--
-- Dumping data for table `Likes`
--

INSERT INTO Likes (party_id, user_id, like_status) VALUES
('1', '1', 1),
('1', '3', 1);

