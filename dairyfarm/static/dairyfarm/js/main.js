document.addEventListener('DOMContentLoaded', function() {
    const rfidForm = document.getElementById('rfid-form');
    const farmerDetailsCard = document.getElementById('farmer-details');

    rfidForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const rfidInput = document.getElementById('rfid');
        const rfid = rfidInput.value;

        try {
            const response = await fetch('/scan-rfid/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `rfid=${rfid}`
            });

            const data = await response.json();
            if (data.success) {
                loadFarmerDetails(rfid);
                farmerDetailsCard.classList.remove('d-none');
            } else {
                alert('Invalid RFID card');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error scanning RFID card');
        }
    });

    async function loadFarmerDetails(rfid) {
        try {
            const response = await fetch(`/get-farmer-details/${rfid}/`);
            const data = await response.json();
            
            const detailsHtml = `
                <div class="farmer-info mb-4">
                    <p><strong>Name:</strong> ${data.farmer.name}</p>
                    <p><strong>Phone:</strong> ${data.farmer.phone}</p>
                    <p><strong>Address:</strong> ${data.farmer.address}</p>
                </div>
                
                <form id="milk-collection-form" class="mt-4">
                    <h6>Collect Milk</h6>
                    <div class="mb-3">
                        <label class="form-label">Quantity (L)</label>
                        <input type="number" class="form-control" name="quantity" step="0.01" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Fat Content (%)</label>
                        <input type="number" class="form-control" name="fat_content" step="0.1" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Session</label>
                        <select class="form-control" name="session" required>
                            <option value="morning">Morning</option>
                            <option value="evening">Evening</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit Collection</button>
                </form>
            `;
            
            farmerDetailsCard.querySelector('.card-body').innerHTML = detailsHtml;
            setupMilkCollectionForm();
        } catch (error) {
            console.error('Error:', error);
            alert('Error loading farmer details');
        }
    }

    function setupMilkCollectionForm() {
        const milkCollectionForm = document.getElementById('milk-collection-form');
        milkCollectionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            try {
                const response = await fetch('/collect-milk/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: new URLSearchParams(formData)
                });

                const data = await response.json();
                if (data.success) {
                    alert('Milk collection recorded successfully');
                    window.location.reload(); // Refresh to update the collections table
                } else {
                    alert('Error recording milk collection');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error submitting milk collection');
            }
        });
    }
}); 