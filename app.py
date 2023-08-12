import os
from flask import Flask, render_template, request, send_from_directory, jsonify
import stripe

app = Flask(__name__)

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'stl', 'dwg'}

# Initialize Stripe with your Stripe Secret Key
stripe.api_key = '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'

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    price = request.json['price']  # Get the price from the request
    # Calculate the price in cents to avoid decimal issues
    amount_cents = int(float(price) * 100)

    try:
        # Create a PaymentIntent on Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='eur'
        )

        return jsonify({'clientSecret': payment_intent.client_secret})
    except stripe.error.StripeError as e:
        return jsonify(error=str(e)), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'We have received your file!'
        else:
            return 'Invalid file format. Only .stl and .dwg files are allowed.'
    return 'Upload failed.'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/calculate_price', methods=['POST'])
def calculate_price():
    length = int(request.form['length'])
    width = int(request.form['width'])
    height = int(request.form['height'])

    # Apply the limits for length, width, and height
    length = min(length, 220)
    width = min(width, 220)
    height = min(height, 250)

    total = length + width + height

    if total <= 250:
        price = 9
    elif total <= 350:
        price = 12
    elif total <= 450:
        price = 15
    else:
        price = 18

    return f'Total price: €{price}'

@app.route('/calculate_price_small_pieces', methods=['POST'])
def calculate_price_small_pieces():
    small_length = int(request.form['small_length'])
    small_width = int(request.form['small_width'])
    small_height = int(request.form['small_height'])

    # Apply the limits for small_length, small_width, and small_height
    small_length = min(small_length, 100)
    small_width = min(small_width, 100)
    small_height = min(small_height, 100)

    total_small_pieces = small_length + small_width + small_height

    price_per_unit = 0
    if total_small_pieces <= 60:
        price_per_unit = 0.2
    elif total_small_pieces <= 80:
        price_per_unit = 0.4
    elif total_small_pieces <= 100:
        price_per_unit = 0.6
    elif total_small_pieces <= 120:
        price_per_unit = 0.8
    elif total_small_pieces <= 140:
        price_per_unit = 1
    elif total_small_pieces <= 160:
        price_per_unit = 1.2
    elif total_small_pieces <= 180:
        price_per_unit = 1.4
    elif total_small_pieces <= 200:
        price_per_unit = 1.6

    return f'Total price per unit: €{price_per_unit}'
    
@app.route('/order', methods=['POST'])
def order():
    price = request.form.get('price')
    # Convert price to cents as Stripe requires the amount in cents
    amount_cents = int(float(price) * 100)

    try:
        # Create a payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='eur',
            description='3D Print Wien Order',
        )
        return render_template('payment.html', client_secret=payment_intent.client_secret)
    except stripe.error.StripeError as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)