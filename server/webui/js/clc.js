let repository = null;
let reasons = {};
let json = null;

async function POST(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify(data)
    });
    return response.json();
}

async function GET(url = '') {

    let js = fetch(url, {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
    }).then((response) => response.json()).catch((f) => {
            console.log("error; " + f);
        }
    );
    return js
}

Number.prototype.pretty = function(fix) {
    if (fix) {
        return String(this.toFixed(fix)).replace(/(\d)(?=(\d{3})+\.)/g, '$1,');
    }
    return String(this.toFixed(0)).replace(/(\d)(?=(\d{3})+$)/g, '$1,');
};

async function add_repo() {
    let repo_url = document.getElementById('repo_url').value;
    let words = document.getElementById('words').value.split(/\r?\n/);
    let excludes = document.getElementById('excludes').value.split(/\r?\n/);
    let excludes_context = document.getElementById('excludes_context').value.split(/\r?\n/);
    let branch = document.getElementById('branch').value;
    let words_dict = {};
    for (let i = 0; i < words.length; i++) {
        let arr = words[i].split(/:/);
        if (arr.length == 2) {
            let k = arr[0].trim();
            let v = arr[1].trim();
            words_dict[k] = v;
        }
    }

    if (!repo_url.endsWith('.git')) {
        alert("Repository URL must end with .git!");
        return
    }
    if (repo_url.length > 10 && repo_url.endsWith('.git')) {
        let rv = await POST('/api/addproject.json', {
            url: repo_url,
            branch: branch,
            excludes: excludes,
            words: words_dict,
            excludes_context: excludes_context,
            branch: branch
        })
        alert(rv.message);
        document.getElementById('add_project').style.display = 'none';
    }
}

async function save_repo_settings() {
    let excludes = document.getElementById('excludes').value.split(/\n/);
    let excludes_context = document.getElementById('excludes_context').value.split(/\n/);
    let bad_words = document.getElementById('words').value.split(/\n/);
    let words = {};
    for (let i = 0; i < bad_words.length; i++) {
        let arr = bad_words[i].split(/:/);
        let k = arr[0].trim();
        let v = arr[1].trim();
        words[k] = v;
    }
    let rv = await POST('/api/settings.json', {
        repo: repository,
        words: words,
        excludes: excludes,
        excludes_context: excludes_context
    });
    alert(rv.message);
}

function show_repo_settings() {
    let d = document.getElementById('settings_parent').style.display;
    if (d == 'none') {
        document.getElementById('settings_parent').style.display='block';
    } else {
        document.getElementById('settings_parent').style.display='none';
    }
}




async function prime_projects_list() {
    let defaults = await GET('/api/defaults.json');

    document.getElementById('excludes').textContent = defaults.excludes.join("\n");
    document.getElementById('excludes_context').textContent = defaults.excludes_context.join("\n");
    let bad_words = [];
    for (let k in defaults.words||{}) {
        bad_words.push(`${k}: ${defaults.words[k]}`);
    }
    document.getElementById('words').textContent = bad_words.join("\n");

    let stats = await GET('/api/all.json');

    let parent = document.getElementById('projects_parent');

    let no_files = 0;
    let no_issues = 0;
    let no_projects = 0;

    for (let repo in stats) {
        let project = stats[repo];
        no_projects++;
        if (!project.status) continue
        let a = document.createElement('a');
        a.setAttribute('href', `analysis.html?project=${repo}`);
        a.innerText = repo;

        let tr = document.createElement('tr');
        tr.setAttribute('class', 'table-row');

        // Project
        let td_project = document.createElement('td');
        td_project.appendChild(a);
        tr.appendChild(td_project);

        // Source
        let td_source = document.createElement('td');
        td_source.innerText = project.source;
        tr.appendChild(td_source);

        // Issues
        let td_issues = document.createElement('td');
        td_issues.setAttribute('class', 'text-right');
        td_issues.innerText = project.status.issues.pretty();
        tr.appendChild(td_issues);

        // Files scanned
        let td_scanned = document.createElement('td');
        td_scanned.setAttribute('class', 'text-right');
        td_scanned.innerText = project.status.files_processed.pretty();
        tr.appendChild(td_scanned);




        parent.appendChild(tr);

    }

}




async function prime_intro() {
    let details = await GET('/api/stats.json');
    details = typeof(details) == 'object' ? details : {stats: details, activity: 'unknown...!'};
    let stats = details.stats;

    document.getElementById('activity').innerText = details.activity;
    let m = details.activity.match(/(\d+)%/);
    if (m) {
        document.getElementById('progress').value = m[1];
    } else {
        document.getElementById('progress').style.display = "none";
    }
    document.getElementById('scanner_active').style.display = "inline";
    document.getElementById('scanner_inactive').style.display = "none";

    let n = 0;
    let parent = document.getElementById('quickstats');

    let no_files = 0;
    let no_issues = 0;
    let no_projects = 0;

    for (let repo in stats) {
        n++;
        no_projects++;
        if (typeof(stats[repo][2][stats[repo][2].length-1]) == 'number') {
            no_issues += stats[repo][2][stats[repo][2].length-1];
            no_files += stats[repo][1][stats[repo][1].length-1];
        }
        if (n > 6) continue
        let a = document.createElement('a');
        a.setAttribute('href', `analysis.html?project=${repo}`);
        let div = document.createElement('div');
        a.appendChild(div);
        div.setAttribute('id', `_quickstats_${repo}`);
        parent.appendChild(a);
        for (let z = 1; z < stats[repo][0].length; z++) {
            stats[repo][0][z] = new Date(stats[repo][0][z]*1000.0);
        }
        c3.generate({
            bindto: div,
            title: {
                text: repo
            },
            size: {
                height: 220,
                width: 600
            },
            axis: {
                x: {
                    type: 'timeseries',
                    tick: {
                        count: 7,
                        format: '%Y-%m-%d'
                    },
                    label: {
                        text: "Time",
                        position: "outer-middle"
                    }
                },
                y: {
                    label: {
                        text: "Issues found",
                        position: "outer-middle"
                    },
                    show: true
                },
                y2: {
                    label: {
                        text: "Files processed",
                        position: "outer-middle"
                    },
                    show: true
                }
            },


            data: {
                x: 'x',
                columns: stats[repo],
                type: 'bar',
                types: {
                    'Files processed': 'line',
                    'Scan duration': 'line',
                },
                groups: [
                    ['data1','data2']
                ],
                axes: {
                    'Scan duration': 'y2',
                    'Files processed': 'y2'
                },
                colors: {
                    'Issues discovered': '#1686d2',
                    'Files processed': '#1cd216',
                    'Scan duration': '#d24b16'
                }
            }
        });

    }
    document.getElementById('quickstats_projects').innerText = no_projects.pretty();
    document.getElementById('quickstats_files').innerText = no_files.pretty();
    document.getElementById('quickstats_issues').innerText = no_issues.pretty();
}


function quickstats(source, ty) {
    let groupings = [];
    if (ty == 'stacked') {
        for (let i = 1; i < json[source].length; i++) {
            groupings.push(json[source][i][0]);
        }
    }

    for (let z = 1; z < json[source][0].length; z++) {
        if (typeof(json[source][0][z]) == 'number') {
            json[source][0][z] = new Date(json[source][0][z] * 1000.0);
        }
    }

    c3.generate({
        bindto: document.getElementById('quickstats'),
        title: {
            text: "Issues over time"
        },
        size: {
            height: 320,
            width: 720
        },
        axis: {
            x: {
                label: {
                    text: "Time",
                    position: "outer-middle"
                },
                type: 'timeseries',
                tick: {
                    count: 7,
                    format: '%Y-%m-%d'
                }
            },
            y2: {
                label: {
                    text: "Files processed",
                    position: "outer-middle"
                },
                show: true
            },
            y: {
                label: {
                    text: "Issues found",
                    position: "outer-middle"
                },
                show: true
            }
        },
        data: {
            x: 'x',
            columns: json[source],
            type: 'bar',
            types: {
                'Files processed': 'line',
                'Scan duration': 'line',
            },
            groups: [
                groupings
            ],
            axes: {
                'Scan duration': 'y2',
                'Files processed': 'y2'
            },
            colors: {
                'Issues discovered': '#1686d2',
                'Files processed': '#1cd216',
                'Scan duration': '#d24b16'
            }
        }
    });
}


async function prime_analysis(limit) {
    document.getElementById('spinner').style.display = 'block';
    document.getElementById('stats').style.display = 'none';
    limit = limit ? limit : 500
    let stats = await GET('/api/details.json' + location.search + "&limit=" + limit);
    json = stats;
    document.getElementById('spinner').style.display = 'none';
    document.getElementById('stats').style.display = 'block';


    let n = 0;
    let parent = document.getElementById('quickstats');

    let no_files = 0;
    let no_issues = 0;
    let no_handled = 0;
    repository = stats.repo;
    reasons = stats.reasons;
    quickstats('chart');

    c3.generate({
        bindto: document.getElementById('quickstats_breakdown'),
        title: {
            text: "Word breakdown"
        },
        size: {
            height: 320,
            width: 480
        },

        data: {
            columns: stats.breakdown,
            type: 'donut'
        },
        tooltip: {
            format: {
                //title: function (d) { return 'Data ' + d; },
                value: function (value, ratio, id) {
                    console.log(value, ratio);
                    return value.pretty() + " (" + (parseInt(ratio*1000) / 10.0) + "%)";
                }
            }
        }
    });


    let excludes = document.getElementById('excludes');
    excludes.textContent = (stats.details.excludes||[]).join("\n");

    let excludes_context = document.getElementById('excludes_context');
    excludes_context.textContent = (stats.details.excludes_context||[]).join("\n");

    let words = document.getElementById('words');
    let bad_words = [];
    for (let k in stats.details.bad_words||{}) {
        bad_words.push(`${k}: ${stats.details.bad_words[k]}`);
    }
    words.textContent = bad_words.join("\n");

    let issues_parent = document.getElementById('issues_parent');
    issues_parent.innerHTML = "";
    for (let i=0; i < stats.issues.length; i++) {
        let issue = stats.issues[i];
        let tr = document.createElement('tr');
        tr.setAttribute('class', 'table-expand-row');
        tr.setAttribute('data-open-details', true);
        tr.setAttribute('title', "Click to see the context in which this word appears");

        // Path
        let td_path = document.createElement('td');
        td_path.innerText = issue.path;
        tr.appendChild(td_path);

        // Line
        let td_line = document.createElement('td');
        td_line.innerText = issue.line;
        tr.appendChild(td_line);

        // Column
        let td_column = document.createElement('td');
        td_column.innerText = issue.mark;
        tr.appendChild(td_column);

        // Word
        let td_word = document.createElement('td');
        td_word.innerText = issue.word;
        tr.appendChild(td_word);

        // Reason
        let td_reason = document.createElement('td');
        td_reason.innerText = issue.reason;
        if (reasons[issue.reason]) {
            td_reason.setAttribute('title', reasons[issue.reason]);
        }
        tr.appendChild(td_reason);

        // Resolution
        let resolution = 'Unresolved';
        if (issue.resolution == 'ignore') resolution = 'Ignore word';
        if (issue.resolution == 'intended') resolution = 'Intended word';
        let td_resolution = document.createElement('td');
        td_resolution.innerText = resolution;
        tr.appendChild(td_resolution);
        if (!issue.resolution) {
            tr.style.color = '#900';
        } else {
            tr.style.color = '#080';
        }

        issues_parent.appendChild(tr);

        tr = document.createElement('tr');
        tr.setAttribute('class', 'table-expand-row-content');
        let td = document.createElement('td');
        td.setAttribute('colspan', '8');
        td.setAttribute('class', 'table-expand-row-nested');
        let p = document.createElement('p');
        p.innerText = issue.context;
        if (issue.word.length > 5) $(p).html($(p).text().replace('<', '&lt;').replace(new RegExp(issue.word, 'i'), (a) => `<strong style="color: #950;">${a.replace('<', '&lt;')}</strong>`));
        else $(p).html($(p).text().replace('<', '&lt;').replace(new RegExp("((\\b|_|\W)" + issue.word + "(ed|ing|s)?(?:\\b|\\W|_)+)", 'i'), (a) => `<strong style="color: #950;">${a.replace('<', '&lt;')}</strong>`));
        td.appendChild(p);
        tr.appendChild(td);
        issues_parent.appendChild(tr);


    }

    if (stats.issues.length == limit) {
        let tr = document.createElement('tr');
        let td = document.createElement('td');
        td.setAttribute('colspan', '7');
        tr.appendChild(td);
        tr.setAttribute('id', 'notice');
        td.innerText = "For speed reasons, only the first 500 issues are listed...";
        let a = document.createElement('a');
        a.innerText = "Click here to show all (might take a while to load)";
        a.setAttribute('href', 'javascript:void(prime_analysis(99999));');
        td.appendChild(a);
        issues_parent.appendChild(tr);
    }



    $('[data-open-details]').click(function (e) {
        e.preventDefault();
        $(this).next().toggleClass('is-active');
        $(this).toggleClass('is-active');
    });

    document.getElementById('quickstats_issues').innerText = stats.details.status.issues.pretty();
    document.getElementById('quickstats_files').innerText = stats.details.status.files_processed.pretty();
    document.getElementById('quickstats_duration').innerText = parseInt(stats.details.status.duration).pretty() + " seconds";
    document.getElementById('quickstats_epoch').innerText = new Date(stats.details.status.epoch*1000.0).toLocaleString();
    document.getElementById('reponame').innerText = stats.details.source;

}


function filter_results(txt) {
    let trs = document.getElementById('issues_parent').getElementsByTagName('tr');
    let re = new RegExp(txt, 'i');
    for (let i = 0; i < trs.length; i++) {
        let tr = trs[i];
        if (tr.getAttribute('class') == 'table-expand-row-content') continue
        if (txt.length == 0 || tr.innerText.match(re)) {
            tr.style.display = "table-row";
        } else {
            tr.style.display = "none";
        }
    }
}