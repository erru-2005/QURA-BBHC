from flask import Blueprint, render_template, request, jsonify
from . import mongo
from bson import ObjectId

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('all_books.html')

@main.route('/statistic', methods=['GET', 'POST'])
def statistics():
    try:
        total_books = None
        issued_books_count = None
        available_books = None
        header = None
        search_type = None

        
        # Always render the page
        return render_template(
            'index.html',
            total_books=total_books,
            issued_books=issued_books_count,
            available_books=available_books,
            header=header,
            search_type=search_type,
        )

    except Exception as e:
        print(f"Error in statistics: {e}")
        return render_template('index.html', error="Error processing search request")

@main.route('/all-books')
def all_books():
    
    
    return render_template('all_books.html', books=books)

@main.route('/api/books')
def get_books():
    try:
        search = request.args.get('q', '').strip()
        department = request.args.get('department', '').strip()
        print(search)
        print(department)
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
                {'barcode': pattern},
                {'department': pattern}
            ]
        
        # Get books with optimized query
        books_cursor = mongo.db.books.find(
            filter_query,
            {'_id': 1, 'title': 1, 'author': 1, 'department': 1, 'barcode': 1, 'accession_number': 1}
        )  # Limit results for performance
        
        books = [{
            **book,
            '_id': str(book['_id']),
            'status': 'available'
        } for book in books_cursor]
        # Check if each book is Available or not
        for book in books:
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
    try:
        print("Search request received")
        data = request.get_json()
        print(data)
        search_type = data.get('searchType', 'Title')
        query = data.get('query', '').strip()
       
        if request.method == "POST":
            if not query or not search_type:
                return render_template(
                    'index.html',
                    error="Please enter both query and search type."
                )

            # Prepare query value based on search type
            if search_type == "Department Code":
                query_value = query.upper()
                db_field = "department_code"
            elif search_type == "Title":
                query_value = query.upper()
                db_field = "title"
            elif search_type == "Author":
                query_value = query.title()
                db_field = "author"
            elif search_type == "Department":
                query_value = query.title()
                db_field = "department"
            else:
                query_value = query
                db_field = "title"

            header = f"{search_type}: {query_value}"

            # Prepare MongoDB filter
            filter_query = {db_field: query_value}
            filter_query_issued = {"book." + db_field: query_value, "status": "issued"}

            # Count total books
            total_books = mongo.db.books.count_documents(filter_query)
            # Count issued books
            issued_books_count = mongo.db.issued_books.count_documents(filter_query_issued)
            # Calculate available books
            available_books = total_books - issued_books_count


        return jsonify({
            'stats': {
                'total': total_books,
                'issued': issued_books_count,
                'available': available_books
            }
        })
        
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    try:
        search_type = request.args.get('type', 'Title')
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify([])
        
        field = {
            'Title': 'title',
            'Author': 'author',
            'Department': 'department',
            'Department Code': 'department_code'
        }.get(search_type, 'title')

        # Create case-insensitive regex pattern
        import re
        pattern = re.compile(f'.*{re.escape(query)}.*', re.IGNORECASE)
        
        # Find matching documents
        matches = mongo.db.books.find(
            {field: pattern},
            {field: 1, '_id': 0}
        ).limit(10)
        
        # Extract unique values
        suggestions = list(set(doc[field] for doc in matches if doc.get(field)))
        
        return jsonify(suggestions)
        
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return jsonify([])