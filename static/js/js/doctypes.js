var doctypesJSON = {
    "article": {
        "Required": [["author","Autor(es)"], ["title","Título"], ["journal","Journal"], ["year","Año"]],
        "Optional": [["volume","Volumen"], ["number","Número"], ["pages","Páginas"], ["month","Mes"], ["note","Nota"],["doi", "DOI"], ["url", "URL"]]
    },
    "book": {
        "Required":[ ["author","Autor(es)"],["editor","Editor(es)"], ["title","Título"], ["publisher","Editorial"], ["year","Año"]],
        "Optional": [["volume","Volumen"],["number","Número"], ["series","Serie"], ["address","Dirección"], ["edition","Edición"], ["month","Mes"], ["note","Nota"], ["url", "URL"]]

    },
    "desarrollo": {
        "Required":[ ["author","Autor(es)es"],["editor","Usuario(s)"], ["title","Título"], ["publisher","Descripción"], ["year","Año"], ["volume","Fecha de registro"],["address","Fecha de aprobación"], ["note","Trascendencia"]],
        "Optional": [["url", "URL"]]
    },
    "patente": {
        "Required":[ ["author","Titular"],["editor","Inventor(es)"], ["title","Título de la patente"], ["publisher","Número de solicitud"], ["year","Año"], ["edition","Fecha de solicitud"],["volume","Fecha de expedición"], ["address","Denominación"], ["note","Vigencia"]],
        "Optional": []
    },
    "booklet": {
        "Required":[ ["title","Título"]], 
        "Optional": [["author","Autor(es)"], ["howpublished","Publicado como"], ["address","Dirección"], ["month","Mes"], ["year","Año"], ["note","Nota"], ["url", "URL"]]
    },
    "inbook": {
        "Required":[ ["author","Autor(es)"],["editor","Editor(es)"], ["title","Título"], ["chapter","Capítulo"], ["pages","Páginas"], ["publisher","Editorial"], ["year","Año"]], 
        "Optional": [["volume","Volumen"],["number","Número"], ["series","Serie"], ["type","Tipo"], ["address","Dirección"], ["edition","Edición"], ["month","Mes"], ["note","Nota"], ["doi", "DOI"], ["url", "URL"] ]
    },
    
    "incollection": {
        "Required":[ ["author","Autor(es)"], ["title","Título"], ["booktitle","Título del libro"], ["publisher","Editoral"], ["year","Año"]],
        "Optional": [["editor","Editor(es)"], ["volume","Volumen"],["number","Número"], ["series","Serie"], ["type","Tipo"], ["chapter","Capítulo"], ["pages","Páginas"], ["address","Dirección"], ["edition","Edición"], ["month","Mes"], ["note","Nota"], ['doi','DOI'], ["url", "URL"]]
    },
    
    "inproceedings": {
        "Required":[ ["author","Autor(es)"], ["title","Título"], ["booktitle","Título del libro"], ["year","Año"]], 
        "Optional": [["editor","Editor(es)"], ["volume","Volumen"],["number","Número"], ["series","Serie"], ["pages","Páginas"], ["address","Dirección"], ["month","Mes"], ["organization","Organización"], ["publisher","Editoral"], ["note","Nota"], ['doi','DOI'], ["url", "URL"]]
    },
    
    "manual": {
        "Required":[ ["title","Título"]], 
        "Optional": [["author","Autor(es)"], ["organization","Organización"], ["address","Dirección"], ["edition","Edición"], ["month","Mes"], ["year","Año"], ["note","Nota"], ["url", "URL"]]
    },
    "comercial": {
        "Required":[ ["title","Título"],["author","Autor(es)es"], ["address","Usuarios"],["note","Descripción"],  ["month","Mes"], ["year","Año"] ], 
        "Optional": [["url", "URL"]]
    },
    "mastersthesis": {
        "Required":[ ["author","Autor(es)"], ["title","Título"], ["school","Institución"], ["address","Director(es)"], ["month","Mes"], ["year","Año"]],
        "Optional": [["type","Tipo"], ["note","Nota"],["url", "URL"]  ]
    },

    "misc": {
        "Required":[["title","Campo Principal"], ["note","Campo Secundario"], ["year","Año"]], 
        "Optional": [["author","Author"], ["month","Mes"],["url", "URL"]]
    },
    
    "phdthesis": {
        "Required": [["author","Autor(es)"], ["title","Título"], ["school","Institución"], ["address","Director(es)"], ["month","Mes"], ["year","Año"]],
        "Optional": [["type","Tipo"], ["note","Nota"],["url", "URL"]]
    },
    
    "proceedings": {
        "Required":[ ["title","Título"], ["year","Año"]], 
        "Optional": [["editor","Editor(es)"], ["volume","Volumen"],["number","Número"], ["series","Serie"], ["address","Dirección"], ["month","Mes"], ["organization","Organización"], ["publisher","Editoral"], ["note","Nota"],["url", "URL"]]
    },
    
    "techreport": {
        "Required":[ ["author","Autor(es)"], ["title","Título"], ["institution","Institución"], ["year","Año"]], 
        "Optional": [["type","Tipo"], ["number","Número"], ["address","Dirección"], ["month","Mes"], ["note","Nota"],["url", "URL"]]
    },
    
    "unpublished": {
        "Required":[ ["author","Nombre"], ["title","Institución"], ["note","Adicional"], ["year","Año"]], 
        "Optional": [["month","Mes"]]
    }
};


const capitalize = (s) => {
    if (typeof s !== 'string') return ''
    return s.charAt(0).toUpperCase() + s.slice(1)
}

function generateUID() {
    // I generate the UID from two parts here 
    // to ensure the random number provide enough bits.
    var firstPart = (Math.random() * 46656) | 0;
    var secondPart = (Math.random() * 46656) | 0;
    firstPart = ("000" + firstPart.toString(36)).slice(-3);
    secondPart = ("000" + secondPart.toString(36)).slice(-3);
    return firstPart + secondPart;
}
