from django import template
from ..models import StudentDocument

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Gets a value from a dictionary using the given key.
    Usage: {{ dictionary|get_item:key }}
    
    This is used in the document matrix view to get a document by its key,
    which is constructed as student_id_document_type_id.
    """
    if dictionary is None:
        print(f"Error in get_item: dictionary is None, key={key}")
        return None
    
    try:
        # Check if the key exists
        found = key in dictionary
        value = dictionary.get(key, None)
        
        # Print debugging info
        if found and value:
            print(f"✅ Found document for key {key}: {value.student.first_name} {value.student.last_name} - {value.document_type.name}")
        elif key and key.strip():
            # Only print if key isn't empty/whitespace
            print(f"❌ No document found for key: {key}")
        
        return value
    except Exception as e:
        # Print any errors that occur
        print(f"Error in get_item with key {key}: {str(e)}")
        return None

@register.simple_tag
def debug_keys(dictionary):
    """
    Prints all keys in the dictionary for debugging.
    Usage: {% debug_keys dictionary %}
    """
    if dictionary:
        print("All keys in dictionary:")
        for key in dictionary.keys():
            print(f"- {key}")
    else:
        print("Dictionary is empty or None")
    return "" 

@register.simple_tag
def get_document(student_id, doc_type_id):
    """
    Get a document by student ID and document type ID
    Usage: {% get_document student.id doc_type.id as document %}
    """
    try:
        # Print for debugging
        print(f"Looking for document with student_id={student_id}, doc_type_id={doc_type_id}")
        
        # Query all documents for this student & document type
        docs = StudentDocument.objects.filter(student_id=student_id, document_type_id=doc_type_id)
        count = docs.count()
        
        if count > 1:
            # If multiple documents found (shouldn't happen), log and return the most recent
            print(f"WARNING: Found {count} documents for student {student_id} and doc_type {doc_type_id}")
            for d in docs:
                print(f"  - ID: {d.id}, Filename: {d.filename}")
            document = docs.order_by('-created_at').first()
            print(f"Returning most recent: {document.id}")
            return document
        elif count == 1:
            # Single document found (expected case)
            document = docs.first()
            print(f"Found document: {document.id}, Filename: {document.filename}")
            return document
        else:
            # No document found
            print(f"No document found for student {student_id} and doc_type {doc_type_id}")
            return None
    except Exception as e:
        print(f"Error getting document: {e}")
        return None 