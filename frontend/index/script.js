const searchIcon = document.getElementById('search-icon');
const searchInput = document.getElementById('search-input');
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const mobileMenu = document.querySelector('.mobile-menu');

searchIcon.addEventListener('click', () => {
  searchInput.classList.toggle('active');
  if (searchInput.classList.contains('active')) {
    searchInput.focus();
  }
});

mobileMenuBtn.addEventListener('click', () => {
  mobileMenu.classList.toggle('active');
  const spans = mobileMenuBtn.querySelectorAll('span');
  
  if (mobileMenu.classList.contains('active')) {
    spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
    spans[1].style.opacity = '0';
    spans[2].style.transform = 'rotate(-45deg) translate(7px, -7px)';
  } else {
    spans[0].style.transform = 'none';
    spans[1].style.opacity = '1';
    spans[2].style.transform = 'none';
  }
});

// Handle search functionality
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    const searchTerm = searchInput.value;
    // Implement your search logic here
    console.log('Searching for:', searchTerm);
    searchInput.value = '';
    searchInput.classList.remove('active');
  }
});