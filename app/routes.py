from flask import Blueprint, render_template, request, jsonify
from . import mongo
from bson import ObjectId

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('all_books.html')

@main.route('/statistic')
def statistics():
    return render_template('index.html')

@main.route('/all-books')
def all_books():
    try:
        # Get all books from MongoDB
        books_cursor = mongo.db.books.find()
        books = []
        
        for book in books_cursor:
            book['_id'] = str(book['_id'])
            # Check if book is issued
            issued_book = mongo.db.issued_books.find_one({
                'book.barcode': book.get('barcode', ''),
                'status': 'issued'
            })
            
            if issued_book:
                book['status'] = 'issued'
                book['issued_to'] = issued_book.get('student', {}).get('studentName', 'Unknown')
            else:
                book['status'] = 'available'
            
            books.append(book)
            
    except Exception as e:
        print(f"Error fetching books: {e}")
        books = []
    
    return render_template('all_books.html', books=books)

@main.route('/api/books')
def get_books():
    try:
        search = request.args.get('q', '').strip()
        department = request.args.get('department', '').strip()
        
        # Build filter query
        filter_query = {}
        if department:
            filter_query['department'] = department
        if search:
            import re
            pattern = re.compile(search, re.IGNORECASE)
            filter_query['$or'] = [
                {'title': pattern},
                {'author': pattern},
                {'isbn': pattern},
                {'department': pattern}
            ]
        
        # Get books with optimized query
        books_cursor = mongo.db.books.find(
            filter_query,
            {'_id': 1, 'title': 1, 'author': 1, 'department': 1, 'isbn': 1, 'department_code': 1}
        ).limit(50)  # Limit results for performance
        
        books = [{
            **book,
            '_id': str(book['_id']),
            'status': 'available'
        } for book in books_cursor]
        
        return jsonify({
            'books': books,
            'total': len(books)
        })
        
    except Exception as e:
        print(f"Error in get_books: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/departments')
def get_departments():
    try:
        departments = mongo.db.books.distinct('department')
        return jsonify(departments)
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return jsonify([])

@main.route('/api/authors')
def get_authors():
    try:
        authors = mongo.db.books.distinct('author')
        return jsonify(authors)
    except Exception as e:
        print(f"Error fetching authors: {e}")
        return jsonify([])

@main.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    search_type = data.get('searchType', 'Title')
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'results': [], 'total': 0})
    
    # Define search fields based on search type
    search_fields = {
        'Title': 'title',
        'Author': 'author',
        'Department': 'department',
        'Department Code': 'department_code'
    }
    
    field = search_fields.get(search_type, 'title')
    
    # Create regex pattern for case-insensitive search
    import re
    pattern = re.compile(query, re.IGNORECASE)
    
    # Search in MongoDB
    results = list(mongo.db.books.find(
        {field: pattern},
        {'_id': 1, 'title': 1, 'author': 1, 'department': 1, 'department_code': 1}
    ).limit(10))
    
    # Convert ObjectId to string for JSON serialization
    for result in results:
        result['_id'] = str(result['_id'])
    
    return jsonify({'results': results, 'total': len(results)})

@main.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    search_type = request.args.get('type', 'Title')
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    # Define search fields based on search type
    search_fields = {
        'Title': 'title',
        'Author': 'author',
        'Department': 'department',
        'Department Code': 'department_code'
    }
    
    field = search_fields.get(search_type, 'title')
    
    # Create regex pattern for case-insensitive search
    import re
    pattern = re.compile(f'^{re.escape(query)}', re.IGNORECASE)
    
    # Get suggestions from MongoDB
    suggestions = list(mongo.db.books.distinct(field, {field: pattern}))
    
    return jsonify(suggestions[:5])  # Limit to 5 suggestions