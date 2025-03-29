-- Database: pharmacy_db
-- Purpose: Complete pharmacy management system with all relationships

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE DATABASE
IF
  NOT EXISTS `pharmacy_db` DEFAULT CHARACTER
  SET utf8mb4 COLLATE utf8mb4_general_ci;
  USE `pharmacy_db`;

  -- --------------------------------------------------------
  -- Table structure for suppliers (must be created first)
  -- --------------------------------------------------------

  CREATE TABLE `suppliers` (
    `supplier_id` int(11) NOT NULL AUTO_INCREMENT
    , `name` varchar(100) NOT NULL
    , `contact_person` varchar(85) DEFAULT NULL
    , `phone` varchar(15) DEFAULT NULL
    , `email` varchar(100) DEFAULT NULL
    , `country` varchar(50) DEFAULT NULL
    , `payment_terms` varchar(100) DEFAULT NULL
    , `created_at` timestamp NOT NULL DEFAULT current_timestamp()
    , `updated_at` timestamp NULL DEFAULT NULL
    ON
    UPDATE
      current_timestamp()
      , PRIMARY KEY (`supplier_id`)
      , UNIQUE KEY `email` (`email`)
      , KEY `name` (`name`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

  -- Sample supplier data
  INSERT INTO
    `suppliers` (
      `supplier_id`
      , `name`
      , `contact_person`
      , `phone`
      , `email`
      , `country`
      , `payment_terms`
    )
  VALUES
    (
      1
      , 'Global Pharma Inc.'
      , 'John Smith'
      , '+11234567890'
      , 'john@globalpharma.com'
      , 'USA'
      , 'Net 30'
    )
    , (
      2
      , 'MediCare Solutions'
      , 'Sarah Johnson'
      , '+441234567890'
      , 'sarah@medicare.com'
      , 'UK'
      , 'Net 45'
    )
    , (
      3
      , 'HealthPlus Ltd.'
      , 'Michael Brown'
      , '+613456789012'
      , 'michael@healthplus.com'
      , 'Australia'
      , 'Net 60'
    );

  -- --------------------------------------------------------
  -- Table structure for medicines (references suppliers)
  -- --------------------------------------------------------

  CREATE TABLE `medicines` (
    `medicine_id` int(11) NOT NULL AUTO_INCREMENT
    , `name` varchar(100) NOT NULL
    , `quantity` int(11) NOT NULL DEFAULT 0
    , `price` decimal(10, 2) NOT NULL
    , `expiry_date` date DEFAULT NULL
    , `manufacturer` varchar(100) DEFAULT NULL
    , `batch_number` varchar(50) DEFAULT NULL
    , `category` varchar(50) DEFAULT NULL
    , `description` text DEFAULT NULL
    , `supplier_id` int(11) DEFAULT NULL
    , `created_at` timestamp NOT NULL DEFAULT current_timestamp()
    , `updated_at` timestamp NULL DEFAULT NULL
    ON
    UPDATE
      current_timestamp()
      , PRIMARY KEY (`medicine_id`)
      , KEY `supplier_id` (`supplier_id`)
      , KEY `name` (`name`)
      , KEY `category` (`category`)
      , KEY `expiry_date` (`expiry_date`)
      , CONSTRAINT `medicines_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`)
    ON DELETE SET NULL
    ON
    UPDATE
      CASCADE
      , CONSTRAINT `positive_quantity` CHECK (`quantity` >= 0)
      , CONSTRAINT `positive_price` CHECK (`price` > 0)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

  -- Sample medicine data
  INSERT INTO
    `medicines` (
      `medicine_id`
      , `name`
      , `quantity`
      , `price`
      , `expiry_date`
      , `manufacturer`
      , `batch_number`
      , `category`
      , `description`
      , `supplier_id`
    )
  VALUES
    (
      1
      , 'Paracetamol 500mg'
      , 200
      , 5.99
      , '2025-12-31'
      , 'Global Pharma Inc.'
      , 'PARA2023A'
      , 'Pain Relief'
      , 'For fever and mild pain relief'
      , 1
    )
    , (
      2
      , 'Ibuprofen 400mg'
      , 150
      , 7.50
      , '2024-11-30'
      , 'MediCare Solutions'
      , 'IBU2023B'
      , 'Pain Relief'
      , 'Anti-inflammatory pain reliever'
      , 2
    )
    , (
      3
      , 'Amoxicillin 250mg'
      , 100
      , 12.99
      , '2024-10-15'
      , 'HealthPlus Ltd.'
      , 'AMOX2023C'
      , 'Antibiotic'
      , 'For bacterial infections'
      , 3
    )
    , (
      4
      , 'Cetirizine 10mg'
      , 180
      , 8.25
      , '2025-06-30'
      , 'Global Pharma Inc.'
      , 'CET2023D'
      , 'Antihistamine'
      , 'For allergy relief'
      , 1
    )
    , (
      5
      , 'Omeprazole 20mg'
      , 120
      , 15.75
      , '2025-03-31'
      , 'MediCare Solutions'
      , 'OME2023E'
      , 'Antacid'
      , 'For acid reflux and heartburn'
      , 2
    );

  -- --------------------------------------------------------
  -- Table structure for customers
  -- --------------------------------------------------------

  CREATE TABLE `customers` (
    `customer_id` int(11) NOT NULL AUTO_INCREMENT
    , `name` varchar(100) NOT NULL
    , `phone` varchar(15) DEFAULT NULL
    , `email` varchar(100) DEFAULT NULL
    , `address` text DEFAULT NULL
    , `age` int(11) DEFAULT NULL
    , `loyalty_points` int(11) DEFAULT 0
    , `created_at` timestamp NOT NULL DEFAULT current_timestamp()
    , `updated_at` timestamp NULL DEFAULT NULL
    ON
    UPDATE
      current_timestamp()
      , PRIMARY KEY (`customer_id`)
      , UNIQUE KEY `email` (`email`)
      , KEY `name` (`name`)
      , CONSTRAINT `positive_loyalty` CHECK (`loyalty_points` >= 0)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

  -- Sample customer data
  INSERT INTO
    `customers` (
      `customer_id`
      , `name`
      , `phone`
      , `email`
      , `address`
      , `age`
      , `loyalty_points`
    )
  VALUES
    (
      1
      , 'David Wilson'
      , '+11234567891'
      , 'david@example.com'
      , '123 Main St, New York'
      , 35
      , 150
    )
    , (
      2
      , 'Emma Johnson'
      , '+441234567891'
      , 'emma@example.com'
      , '456 High St, London'
      , 28
      , 75
    )
    , (
      3
      , 'Mohammed Ali'
      , '+613456789123'
      , 'mohammed@example.com'
      , '789 George St, Sydney'
      , 42
      , 200
    );

  -- --------------------------------------------------------
  -- Table structure for employees
  -- --------------------------------------------------------

  CREATE TABLE `employees` (
    `employee_id` int(11) NOT NULL AUTO_INCREMENT
    , `name` varchar(100) NOT NULL
    , `role` varchar(50) DEFAULT NULL
    , `phone` varchar(15) DEFAULT NULL
    , `email` varchar(100) DEFAULT NULL
    , `salary` decimal(10, 2) DEFAULT NULL
    , `hire_date` date DEFAULT NULL
    , `created_at` timestamp NOT NULL DEFAULT current_timestamp()
    , `updated_at` timestamp NULL DEFAULT NULL
    ON
    UPDATE
      current_timestamp()
      , PRIMARY KEY (`employee_id`)
      , UNIQUE KEY `email` (`email`)
      , KEY `name` (`name`)
      , KEY `role` (`role`)
      , CONSTRAINT `positive_salary` CHECK (`salary` > 0)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

  -- Sample employee data
  INSERT INTO
    `employees` (
      `employee_id`
      , `name`
      , `role`
      , `phone`
      , `email`
      , `salary`
      , `hire_date`
    )
  VALUES
    (
      1
      , 'Robert Smith'
      , 'Pharmacist'
      , '+11234567892'
      , 'robert@pharmacy.com'
      , 6500.00
      , '2020-01-15'
    )
    , (
      2
      , 'Sarah Williams'
      , 'Sales Associate'
      , '+441234567892'
      , 'sarah@pharmacy.com'
      , 3200.00
      , '2021-05-20'
    )
    , (
      3
      , 'James Brown'
      , 'Manager'
      , '+613456789234'
      , 'james@pharmacy.com'
      , 8500.00
      , '2019-03-10'
    );

  -- --------------------------------------------------------
  -- Table structure for sales (references medicines, customers, employees)
  -- --------------------------------------------------------

  CREATE TABLE `sales` (
    `sale_id` int(11) NOT NULL AUTO_INCREMENT
    , `medicine_id` int(11) NOT NULL
    , `quantity` int(11) NOT NULL
    , `unit_price` decimal(10, 2) NOT NULL
    , `total_price` decimal(10, 2) NOT NULL
    , `sale_date` timestamp NOT NULL DEFAULT current_timestamp()
    , `customer_id` int(11) DEFAULT NULL
    , `employee_id` int(11) DEFAULT NULL
    , `created_at` timestamp NOT NULL DEFAULT current_timestamp()
    , `updated_at` timestamp NULL DEFAULT NULL
    ON
    UPDATE
      current_timestamp()
      , PRIMARY KEY (`sale_id`)
      , KEY `medicine_id` (`medicine_id`)
      , KEY `customer_id` (`customer_id`)
      , KEY `employee_id` (`employee_id`)
      , CONSTRAINT `sales_ibfk_1` FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`medicine_id`)
    ON DELETE CASCADE
    , CONSTRAINT `sales_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
    ON DELETE SET NULL
    , CONSTRAINT `sales_ibfk_3` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`)
    ON DELETE SET NULL
    , CONSTRAINT `positive_sale_quantity` CHECK (`quantity` > 0)
    , CONSTRAINT `positive_sale_price` CHECK (
      `unit_price` > 0
      AND `total_price` > 0
    )
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

  -- Sample sales data showing all relationships
  INSERT INTO
    `sales` (
      `sale_id`
      , `medicine_id`
      , `quantity`
      , `unit_price`
      , `total_price`
      , `sale_date`
      , `customer_id`
      , `employee_id`
    )
  VALUES
    (1, 1, 2, 5.99, 11.98, '2023-01-15 10:30:00', 1, 1)
    , (2, 2, 1, 7.50, 7.50, '2023-01-15 11:15:00', 2, 2)
    , (3, 3, 3, 12.99, 38.97, '2023-01-16 09:45:00', 3, 3)
    , (4, 4, 1, 8.25, 8.25, '2023-01-16 14:20:00', 1, 2)
    , (5, 5, 2, 15.75, 31.50, '2023-01-17 16:10:00', 2, 1);

  -- --------------------------------------------------------
  -- Table structure for prescriptions (optional enhancement)
  -- --------------------------------------------------------

  CREATE TABLE `prescriptions` (
    `prescription_id` int(11) NOT NULL AUTO_INCREMENT
    , `customer_id` int(11) NOT NULL
    , `doctor_name` varchar(100) DEFAULT NULL
    , `doctor_license` varchar(50) DEFAULT NULL
    , `issue_date` date NOT NULL
    , `expiry_date` date DEFAULT NULL
    , `notes` text DEFAULT NULL
    , `created_at` timestamp NOT NULL DEFAULT current_timestamp()
    , `updated_at` timestamp NULL DEFAULT NULL
    ON
    UPDATE
      current_timestamp()
      , PRIMARY KEY (`prescription_id`)
      , KEY `customer_id` (`customer_id`)
      , CONSTRAINT `prescriptions_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
    ON DELETE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

  -- Sample prescription data
  INSERT INTO
    `prescriptions` (
      `prescription_id`
      , `customer_id`
      , `doctor_name`
      , `doctor_license`
      , `issue_date`
      , `expiry_date`
      , `notes`
    )
  VALUES
    (
      1
      , 1
      , 'Dr. Emily Wilson'
      , 'MD12345'
      , '2023-01-10'
      , '2023-04-10'
      , 'For chronic back pain'
    )
    , (
      2
      , 2
      , 'Dr. Michael Johnson'
      , 'MD67890'
      , '2023-01-12'
      , '2023-04-12'
      , 'Seasonal allergies'
    )
    , (
      3
      , 3
      , 'Dr. Sarah Brown'
      , 'MD54321'
      , '2023-01-14'
      , '2023-04-14'
      , 'Post-surgery recovery'
    );

  -- --------------------------------------------------------
  -- Table structure for prescription_items (optional enhancement)
  -- --------------------------------------------------------

  CREATE TABLE `prescription_items` (
    `item_id` int(11) NOT NULL AUTO_INCREMENT
    , `prescription_id` int(11) NOT NULL
    , `medicine_id` int(11) NOT NULL
    , `quantity` int(11) NOT NULL
    , `dosage` varchar(50) DEFAULT NULL
    , `instructions` text DEFAULT NULL
    , `created_at` timestamp NOT NULL DEFAULT current_timestamp()
    , `updated_at` timestamp NULL DEFAULT NULL
    ON
    UPDATE
      current_timestamp()
      , PRIMARY KEY (`item_id`)
      , KEY `prescription_id` (`prescription_id`)
      , KEY `medicine_id` (`medicine_id`)
      , CONSTRAINT `prescription_items_ibfk_1` FOREIGN KEY (`prescription_id`) REFERENCES `prescriptions` (`prescription_id`)
    ON DELETE CASCADE
    , CONSTRAINT `prescription_items_ibfk_2` FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`medicine_id`)
    ON DELETE CASCADE
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

  -- Sample prescription items data
  INSERT INTO
    `prescription_items` (
      `item_id`
      , `prescription_id`
      , `medicine_id`
      , `quantity`
      , `dosage`
      , `instructions`
    )
  VALUES
    (
      1
      , 1
      , 2
      , 30
      , '400mg'
      , 'Take one tablet every 8 hours as needed for pain'
    )
    , (
      2
      , 2
      , 4
      , 60
      , '10mg'
      , 'Take one tablet daily at bedtime'
    )
    , (
      3
      , 3
      , 3
      , 20
      , '250mg'
      , 'Take one capsule every 12 hours for 10 days'
    );

  -- --------------------------------------------------------
  -- Set auto-increment values
  -- --------------------------------------------------------

  ALTER TABLE `suppliers` AUTO_INCREMENT = 4;
  ALTER TABLE `medicines` AUTO_INCREMENT = 6;
  ALTER TABLE `customers` AUTO_INCREMENT = 4;
  ALTER TABLE `employees` AUTO_INCREMENT = 4;
  ALTER TABLE `sales` AUTO_INCREMENT = 6;
  ALTER TABLE `prescriptions` AUTO_INCREMENT = 4;
  ALTER TABLE `prescription_items` AUTO_INCREMENT = 4;

  COMMIT;