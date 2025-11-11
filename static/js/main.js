// Funciones JavaScript básicas
document.addEventListener('DOMContentLoaded', function() {
    // Validación de porcentajes
    const testSizeInput = document.getElementById('test_size');
    const valSizeInput = document.getElementById('val_size');
    
    if (testSizeInput && valSizeInput) {
        testSizeInput.addEventListener('change', function() {
            if (this.value > 90) this.value = 90;
            if (this.value < 1) this.value = 1;
        });
        
        valSizeInput.addEventListener('change', function() {
            if (this.value > 90) this.value = 90;
            if (this.value < 1) this.value = 1;
        });
    }
});