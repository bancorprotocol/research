//
// jarallax.js
//

// Closing an alert changes height of document, so readjust position of parallax elements

import jQuery from 'jquery';
import jarallax from 'bancor_research/bancor_analytics/theme/js/mrare/jarallax';

(($) => {
  if (typeof jarallax === 'function') {
    $('.alert-dismissible').on('closed.bs.alert', () => {
      jarallax(document.querySelectorAll('[data-jarallax]'), 'onScroll');
    });

    $(document).on('resized.mr.overlayNav', () => {
      jarallax(document.querySelectorAll('[data-jarallax]'), 'onResize');
    });

    jarallax(document.querySelectorAll('[data-jarallax]'), {
      disableParallax: /iPad|iPhone|iPod|Android/,
      disableVideo: /iPad|iPhone|iPod|Android/,
    });
  }
})(jQuery);
