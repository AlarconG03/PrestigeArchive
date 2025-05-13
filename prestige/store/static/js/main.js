// Menú móvil
const menuToggle = document.getElementById('menu-toggle');
const closeMenu = document.getElementById('close-menu');
const mobileMenu = document.getElementById('mobile-menu');

if (menuToggle && closeMenu && mobileMenu) {
    menuToggle.addEventListener('click', () => {
        mobileMenu.classList.add('active');
        document.body.style.overflow = 'hidden';
    });
    
    closeMenu.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
    });
}

// Búsqueda móvil
const mobileSearchToggle = document.querySelector('.mobile-search-toggle');
const closeSearch = document.getElementById('close-search');
const mobileSearch = document.getElementById('mobile-search');

if (mobileSearchToggle && closeSearch && mobileSearch) {
    mobileSearchToggle.addEventListener('click', () => {
        mobileSearch.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Enfocar el campo de búsqueda
        const searchInput = mobileSearch.querySelector('.search-input');
        if (searchInput) {
            setTimeout(() => {
                searchInput.focus();
            }, 300);
        }
    });
    
    closeSearch.addEventListener('click', () => {
        mobileSearch.classList.remove('active');
        document.body.style.overflow = '';
    });
}

// Animación de aparición para productos
document.addEventListener('DOMContentLoaded', () => {
    const animateElements = (elements, delay = 100) => {
        elements.forEach((el, index) => {
            setTimeout(() => {
                el.classList.add('fade-in');
            }, index * delay);
        });
    };
    
    // Animar productos
    const productCards = document.querySelectorAll('.product-card');
    if (productCards.length) {
        productCards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        });
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const cards = Array.from(productCards);
                    cards.forEach((card, index) => {
                        setTimeout(() => {
                            card.style.opacity = '1';
                            card.style.transform = 'translateY(0)';
                        }, index * 100);
                    });
                    observer.disconnect();
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(document.querySelector('.products-grid'));
    }
    
    // Animar categorías
    const categoryCards = document.querySelectorAll('.category-card');
    if (categoryCards.length) {
        categoryCards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        });
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const cards = Array.from(categoryCards);
                    cards.forEach((card, index) => {
                        setTimeout(() => {
                            card.style.opacity = '1';
                            card.style.transform = 'translateY(0)';
                        }, index * 100);
                    });
                    observer.disconnect();
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(document.querySelector('.categories-grid'));
    }
});

// Carrito de compras
const addToCartButtons = document.querySelectorAll('.btn-add-cart');
if (addToCartButtons.length) {
    addToCartButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Obtener información del producto
            const productCard = button.closest('.product-card');
            const productName = productCard.querySelector('.product-title').textContent;
            const productPrice = productCard.querySelector('.product-price').textContent;
            
            // Animación de añadir al carrito
            const cartCount = document.querySelector('.cart-count');
            if (cartCount) {
                const currentCount = parseInt(cartCount.textContent);
                cartCount.textContent = currentCount + 1;
                
                // Efecto visual
                cartCount.classList.add('pulse');
                setTimeout(() => {
                    cartCount.classList.remove('pulse');
                }, 300);
                
                // Mostrar notificación
                showNotification(`${productName} añadido al carrito`);
            }
        });
    });
}

// Función para mostrar notificaciones
function showNotification(message) {
    // Comprobar si ya existe una notificación
    let notification = document.querySelector('.notification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.className = 'notification';
        document.body.appendChild(notification);
        
        // Estilos para la notificación
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.right = '20px';
        notification.style.backgroundColor = 'var(--color-brown)';
        notification.style.color = 'white';
        notification.style.padding = '12px 20px';
        notification.style.borderRadius = '4px';
        notification.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        notification.style.zIndex = '1000';
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        notification.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    }
    
    notification.textContent = message;
    
    // Mostrar la notificación
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        
        // Eliminar del DOM después de la transición
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Añadir estilos de animación al CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 0.3s ease-in-out;
    }
`;
document.head.appendChild(style);

// Funciones para el selector de idioma
function toggleLanguageDropdown() {
    const dropdown = document.getElementById('languageDropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}

function changeLanguage(lang) {
    document.getElementById('languageInput').value = lang;
    document.querySelector('.language-form').submit();
}

// Cerrar el dropdown cuando se hace clic fuera de él
document.addEventListener('click', function(event) {
    const container = document.querySelector('.language-selector-container');
    const dropdown = document.getElementById('languageDropdown');
    
    if (container && !container.contains(event.target) && dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
    }
});
