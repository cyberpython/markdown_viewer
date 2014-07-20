$( document ).ready(function() {
    
    $("body").prepend( "<div id='toc'></div>" );
    
    //$('#toc').hide();
    
    $('#markdown_content').toggleClass('with_offset_for_toc');
    $('#markdown_content').attr('margin-left', $('#toc').width()+"px");
    
    $('#toc').toc({
        'selectors': 'h2,h3,h4,h5'
    });
});
