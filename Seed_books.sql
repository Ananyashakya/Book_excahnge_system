-- ─────────────────────────────────────────────────────────────
--  BookSwap — Sample Book Data (50 books across 8 genres)
--  Run this after python main.py has created the tables.
-- ─────────────────────────────────────────────────────────────

USE BookExchangeDB;

-- Create library user if not exists
INSERT IGNORE INTO users (id, name, email, password, is_admin)
VALUES (2, 'BookSwap Library', 'library@bookswap.com', SHA2('library123', 256), 0);

-- Clear old sample data
DELETE FROM books WHERE owner_id = 2;

-- ── Classic Fiction (8) ───────────────────────────────────────
INSERT INTO books (title, author, genre, condition_, owner_id, is_available) VALUES
('To Kill a Mockingbird',        'Harper Lee',             'Classic Fiction', 'Like New', 2, 1),
('1984',                         'George Orwell',          'Classic Fiction', 'Good',     2, 1),
('The Great Gatsby',             'F. Scott Fitzgerald',    'Classic Fiction', 'Good',     2, 1),
('Pride and Prejudice',          'Jane Austen',            'Classic Fiction', 'Fair',     2, 1),
('The Catcher in the Rye',       'J.D. Salinger',          'Classic Fiction', 'Good',     2, 1),
('Brave New World',              'Aldous Huxley',          'Classic Fiction', 'Like New', 2, 1),
('Crime and Punishment',         'Fyodor Dostoevsky',      'Classic Fiction', 'Fair',     2, 1),
('Jane Eyre',                    'Charlotte Bronte',       'Classic Fiction', 'Good',     2, 1),

-- ── Fantasy (8) ───────────────────────────────────────────────
('Harry Potter and the Sorcerers Stone', 'J.K. Rowling',  'Fantasy',         'Good',     2, 1),
('The Hobbit',                   'J.R.R. Tolkien',         'Fantasy',         'Good',     2, 1),
('The Fellowship of the Ring',   'J.R.R. Tolkien',         'Fantasy',         'Like New', 2, 1),
('A Game of Thrones',            'George R.R. Martin',     'Fantasy',         'Good',     2, 1),
('The Name of the Wind',         'Patrick Rothfuss',       'Fantasy',         'Like New', 2, 1),
('Mistborn The Final Empire',    'Brandon Sanderson',      'Fantasy',         'Good',     2, 1),
('The Way of Kings',             'Brandon Sanderson',      'Fantasy',         'Fair',     2, 1),
('American Gods',                'Neil Gaiman',            'Fantasy',         'Good',     2, 1),

-- ── Self Help (8) ─────────────────────────────────────────────
('Atomic Habits',                'James Clear',            'Self Help',       'Like New', 2, 1),
('Rich Dad Poor Dad',            'Robert Kiyosaki',        'Self Help',       'Good',     2, 1),
('Think and Grow Rich',          'Napoleon Hill',          'Self Help',       'Good',     2, 1),
('The Monk Who Sold His Ferrari','Robin Sharma',            'Self Help',       'Like New', 2, 1),
('The 7 Habits of Highly Effective People', 'Stephen Covey', 'Self Help',    'Fair',     2, 1),
('Deep Work',                    'Cal Newport',            'Self Help',       'Like New', 2, 1),
('The Power of Now',             'Eckhart Tolle',          'Self Help',       'Good',     2, 1),
('Ikigai',                       'Hector Garcia',          'Self Help',       'Like New', 2, 1),

-- ── Mystery / Thriller (7) ────────────────────────────────────
('The Da Vinci Code',            'Dan Brown',              'Mystery',         'Fair',     2, 1),
('Gone Girl',                    'Gillian Flynn',          'Mystery',         'Good',     2, 1),
('The Girl with the Dragon Tattoo', 'Stieg Larsson',       'Mystery',         'Good',     2, 1),
('And Then There Were None',     'Agatha Christie',        'Mystery',         'Like New', 2, 1),
('The Silent Patient',           'Alex Michaelides',       'Mystery',         'Like New', 2, 1),
('Big Little Lies',              'Liane Moriarty',         'Mystery',         'Good',     2, 1),
('In the Woods',                 'Tana French',            'Mystery',         'Fair',     2, 1),

-- ── Non-Fiction (7) ───────────────────────────────────────────
('Sapiens',                      'Yuval Noah Harari',      'Non-Fiction',     'Like New', 2, 1),
('Homo Deus',                    'Yuval Noah Harari',      'Non-Fiction',     'Good',     2, 1),
('A Brief History of Time',      'Stephen Hawking',        'Non-Fiction',     'Good',     2, 1),
('The Selfish Gene',             'Richard Dawkins',        'Non-Fiction',     'Fair',     2, 1),
('Educated',                     'Tara Westover',          'Non-Fiction',     'Like New', 2, 1),
('Becoming',                     'Michelle Obama',         'Non-Fiction',     'Like New', 2, 1),
('The Diary of a Young Girl',    'Anne Frank',             'Non-Fiction',     'Good',     2, 1),

-- ── Science Fiction (6) ───────────────────────────────────────
('Dune',                         'Frank Herbert',          'Science Fiction', 'Good',     2, 1),
('The Hitchhikers Guide to the Galaxy', 'Douglas Adams',   'Science Fiction', 'Good',     2, 1),
('Enders Game',                  'Orson Scott Card',       'Science Fiction', 'Like New', 2, 1),
('The Martian',                  'Andy Weir',              'Science Fiction', 'Good',     2, 1),
('Fahrenheit 451',               'Ray Bradbury',           'Science Fiction', 'Fair',     2, 1),
('Neuromancer',                  'William Gibson',         'Science Fiction', 'Good',     2, 1),

-- ── Romance (3) ───────────────────────────────────────────────
('The Notebook',                 'Nicholas Sparks',        'Romance',         'Good',     2, 1),
('Me Before You',                'Jojo Moyes',             'Romance',         'Like New', 2, 1),
('The Fault in Our Stars',       'John Green',             'Romance',         'Good',     2, 1),

-- ── Biography (3) ─────────────────────────────────────────────
('Steve Jobs',                   'Walter Isaacson',        'Biography',       'Good',     2, 1),
('Elon Musk',                    'Ashlee Vance',           'Biography',       'Like New', 2, 1),
('Leonardo da Vinci',            'Walter Isaacson',        'Biography',       'Good',     2, 1);

-- ── Verify ────────────────────────────────────────────────────
SELECT COUNT(*) AS total_books FROM books;
SELECT genre, COUNT(*) AS count FROM books GROUP BY genre ORDER BY count DESC;