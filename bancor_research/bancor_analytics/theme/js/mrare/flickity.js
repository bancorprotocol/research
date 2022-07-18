//
//
// flickity.js
//
// Reset size of flickity sliders embedded in modals

import jQuery from 'jquery';
import 'bancor_research/bancor_analytics/theme/js/mrare/flickity';

(() => {
  $(document).on('shown.bs.modal layoutComplete', (e) => {
    const flickityInstance = $(e.target).find('[data-flickity]');
    flickityInstance.each((index, instance) => {
      const $instance = $(instance);
      if ($instance.data().flickity.isInitActivated) {
        $instance.flickity('resize');
      }
    });
  });
})(jQuery);
