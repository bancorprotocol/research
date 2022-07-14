(function() {
    "use strict";



    $("#menu").metisMenu();

    $('.nk-nav-scroll').slimscroll({
        position: "left",
        size: "5px",
        height: "100%",
    });


    $(".nav-control").click(function() {
        $("body").toggleClass("nav-mini");
        $(".hamburger").toggleClass("is-active");
    });


    $(function() {
        for (var nk = window.location, o = $("ul#menu a").filter(function() {
                    return this.href == nk;
                })
                .addClass("active")
                .parent()
                .addClass("active");;) {
            if (!o.is("li")) break;
            o = o.parent()
                .addClass("in")
                .parent()
                .addClass("active");
        }
    });

    $(function() {
        var win = window.innerWidth;
        if (win <= 1170) {
            $("body").addClass("nav-mini");

        } else {
            $("body").removeClass("nav-mini");
        };


    });

    // $('body').attr('class', 'NewID') 



})(jQuery);




jQuery(window).on("load", function() {
    if ($("#preloader")[0]) {
        $("#preloader").delay(500).fadeOut(500, 0, function() {
            $(this).remove();
        });
    }
});



/////////////////////
//Charts
/////////////////////

// $.plot('#flotPie2', piedata, {
//     series: {
//         pie: {
//             show: true,
//             radius: 1,
//             innerRadius: 0.5,
//             label: {
//                 show: true,
//                 radius: 2 / 3,
//                 formatter: labelFormatter,
//                 threshold: 0.1
//             }
//         }
//     },
//     grid: {
//         hoverable: true,
//         clickable: true
//     }
// });