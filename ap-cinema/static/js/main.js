document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    
    // تغییر ظاهر هدر هنگام اسکرول
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('shadow-md', 'py-2');
            header.classList.remove('py-4');
        } else {
            header.classList.remove('shadow-md', 'py-2');
            header.classList.add('py-4');
        }
    });

    console.log("سامانه سینما شریف با موفقیت لود شد. 🎬");
});