window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['$$', '$$'], ['\\(', '\\)']],
  },
  startup: {
    typeset: false,
  },
  svg: {
    fontCache: 'global'
  }
};

(function () {
  var script = document.createElement('script');
  script.src = 'static/js/mathjax/mathjax-es5-tex-chtml@3.2.2.min.js';
  script.async = true;
  document.head.appendChild(script);
})();
