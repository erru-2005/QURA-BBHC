from app import create_app
# import services.import_books_from_excel 
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 