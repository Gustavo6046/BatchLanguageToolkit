writing = 0;
pending = null;
word = null;
formHideLeft = 0;
hidden = true;

setInterval(function() {
    if ( writing == 0 && pending != null )
    {
        pending();
        pending = null;
    }
    
    writing = Math.max(writing - 1, 0);
}, 50);

examples = [
    'boridnkan',
    'boran',
    'sdokan',
    'dorikan',
    'boyala',
    'parkala',
    'nekenen',
    'bitufon',
    'liscufon',
    'liscumika',
]

addWord = function addWord(lword)
{
    word = lword;
    document.getElementById('form-latko').value = examples[Math.floor(Math.random() * examples.length)];
    document.getElementById('form-composites').value = "red sphere food";
    showForm();
}

addRadical = function addRadical(latko)
{
    $.post({
        url: "./addradical",
        contentType: "application/json;charset=UTF-8",
        dataType: "text",
        data: JSON.stringify({
            key: word,
            value: latko
        }),
        success: function(data, status, req) { setTimeout(translate, 100); }
    });
    hideForm();
}

addComposite = function addComposite(words)
{
    $.post({
        url: "./addcomposite",
        contentType: "application/json;charset=UTF-8",
        dataType: "text",
        data: JSON.stringify({
            key: word,
            radicals: words
        }),
        success: function(data, status, req) { setTimeout(translate, 100) }
    });
    hideForm();
}

showForm = function showForm()
{
    var interv = null;
    var pos = formHideLeft;
    
    hidden = false;
    
    function show()
    {
        if ( pos >= 0 )
        {
            document.getElementById('addForm').style.left = '0px';
            clearInterval(interv);
        }
        
        else
        {
            pos += 5;
            document.getElementById('addForm').style.left = pos + "px";
        }
    }

    if ( word != null )
        interv = setInterval(show, 5);
}

hideForm = function hideForm()
{
    var interv = null;
    var pos = 0;
    
    hidden = true;

    function hide()
    {
        if ( pos < formHideLeft )
        {
            document.getElementById('addForm').style.left = formHideLeft + 'px';
            clearInterval(interv);
        }
        
        else
        {
            pos -= 5;
            document.getElementById('addForm').style.left = pos + "px";
        }
    }
    
    interv = setInterval(hide, 5);
}

translate = function translate(data, target)
{
    if ( target.innerHTML.length == 0 ) target.innerHTML = '...';
    pending = function() {
        $.post({
            url: "./translate",
            data: JSON.stringify({data: data}, null, '\t'),
            contentType: "application/json;charset=UTF-8",
            success: function(data, status, req)
            {
                data = data.replace(/\(rad\.(.+?)\?\)/g, '<span class="unknown-rad" onclick="addWord(\'$1\'.toLowerCase()); return false">&lt;$1?&gt;</span>')
                data = data.replace(/\((.+?)\?\)/g, "")
                target.innerHTML = data;
                writing = false;
            }
        });
    };
    writing = 2;
}