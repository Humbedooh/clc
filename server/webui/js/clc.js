let repository = null;
let reasons = {};
let details_json = null;
let projects_json = null;
let defaults_json = null;
let stats_json = null;
let sort_order = -1;

// Async POST to API
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

// Async GET from API
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

// Prettifier for large numbers (adds commas)
Number.prototype.pretty = function(fix) {
    if (fix) {
        return String(this.toFixed(fix)).replace(/(\d)(?=(\d{3})+\.)/g, '$1,');
    }
    return String(this.toFixed(0)).replace(/(\d)(?=(\d{3})+$)/g, '$1,');
};

// Adds a repo to the service
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
    if (!repo_url.match(/^(https?:\/\/|git:\/\/|ssh:)/)) {
        alert("Repository URL must start with http(s)://, ssh: or git://");
        return
    }
    // Typically, a git URL ends in .git. We have this check to notify people if they try to check out a potentially wrong URL.
    if (!repo_url.endsWith('.git')) {
        if (!confirm("You are trying to check out a repository URL that does not end in .git. Are you sure this is what you intended?")) return
    }
    // Minimum URL size: git:a.bc:d
    if (repo_url.length > 10) {
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

// Adds a repo to the service
async function add_org() {
    let provider = document.getElementById('org_provider').value;
    let orgid = document.getElementById('org_id').value;
    let words = document.getElementById('org_words').value.split(/\r?\n/);
    let excludes = document.getElementById('org_excludes').value.split(/\r?\n/);
    let excludes_context = document.getElementById('org_excludes_context').value.split(/\r?\n/);
    let branch = '';
    let words_dict = {};
    for (let i = 0; i < words.length; i++) {
        let arr = words[i].split(/:/);
        if (arr.length == 2) {
            let k = arr[0].trim();
            let v = arr[1].trim();
            words_dict[k] = v;
        }
    }
    if (!orgid.match(/^([A-Za-z0-9]+)/)) {
        alert("Org ID must be alphanumerical only");
        return
    }

    if (orgid.length > 1) {
        let rv = await POST('/api/addorg.json', {
            provider: provider,
            id: orgid,
            branch: branch,
            excludes: excludes,
            words: words_dict,
            excludes_context: excludes_context
        })
        alert(rv.message);
        document.getElementById('add_org').style.display = 'none';
    }
}


// Saves/updates repository settings
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


async function prime_projects_list(sortkey=0) {
    let defaults = defaults_json ? defaults_json : await GET('/api/defaults.json');
    defaults_json = defaults;

    document.getElementById('excludes').textContent = defaults.excludes.join("\n");
    document.getElementById('excludes_context').textContent = defaults.excludes_context.join("\n");
    document.getElementById('org_excludes').textContent = defaults.excludes.join("\n");
    document.getElementById('org_excludes_context').textContent = defaults.excludes_context.join("\n");
    let bad_words = [];
    for (let k in defaults.words||{}) {
        bad_words.push(`${k}: ${defaults.words[k]}`);
    }
    document.getElementById('words').textContent = bad_words.join("\n");
    document.getElementById('org_words').textContent = bad_words.join("\n");

    let stats = projects_json ? projects_json : await GET('/api/all.json');
    projects_json = stats;

    let parent = document.getElementById('projects_parent');
    parent.innerHTML = "";

    let no_projects = 0;

    let rows = [];

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

        rows.push(tr);

    }

    sort_order *= -1;
    rows.sort((a,b) => {
            let x = a.childNodes[sortkey].textContent.replace(',', '');
            let y = b.childNodes[sortkey].textContent.replace(',', '');
            x = parseInt(x) ? parseInt(x) : x;
            y = parseInt(y) ? parseInt(y) : y;
            return x == y ? 0 : y > x ? -1*sort_order : 1*sort_order
        }
    )

    for (let i = 0; i < rows.length; i++) {
        parent.appendChild(rows[i]);
    }

}




async function prime_intro() {
    let details = stats_json ?  stats_json : await GET('/api/stats.json');
    stats_json = details;
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
    details_json = {};

    for (let repo in stats) {
        n++;
        no_projects++;
        if (typeof(stats[repo][1][stats[repo][1].length-1]) == 'number') {
            no_issues += stats[repo][1][stats[repo][1].length-1];
            no_files += stats[repo][0][stats[repo][0].length-1][1];
        }
        if (n > 9) continue
        let a = document.createElement('a');
        a.setAttribute('href', `analysis.html?project=${repo}`);
        let div = document.createElement('div');
        a.appendChild(div);
        div.setAttribute('id', `_quickstats_${repo}`);
        div.style.width = "400px";
        div.style.height = "180px";
        parent.appendChild(a);
        details_json['breakdown_' + repo] = stats[repo];
        stacked_breakdown('breakdown_' + repo, div, repo, false);

    }
    document.getElementById('quickstats_projects').innerText = no_projects.pretty();
    document.getElementById('quickstats_files').innerText = no_files.pretty();
    document.getElementById('quickstats_issues').innerText = no_issues.pretty();
}


function donut_breakdown() {
    let chartDom = document.getElementById('quickstats_donut');
    chartDom.style.width = "340px";
    chartDom.style.height = "250px";
    let myChart = echarts.init(chartDom);
    let items = [];
    let words = [];
    for (let z= 0; z < details_json.breakdown.length; z++) {
        let word = details_json.breakdown[z][0];
        let val = details_json.breakdown[z][1];
        words.push(word);
        items.push({
            name: word,
            value: val
        });
    }
    items = items.sort((a,b) => b.value - a.value);
    let options = {
        tooltip: {
            trigger: 'item',
            axisPointer: {            // Use axis to trigger tooltip
                type: 'shadow'        // 'shadow' as default; can also be 'line' or 'shadow'
            }
        },
        title: {
            text: "Current word breakdown",
            left: 'center'
        },
        series: {
            name: 'Word breakdown',
            type: 'pie',
            radius: ['30%', '60%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 4,
                borderColor: '#fff',
                borderWidth: 1
            },
            label: {
                show: true
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: '15',
                    fontWeight: 'bold'
                }
            },
            data: items
        }
    };
    myChart.setOption(options);
}


function radar_breakdown(stats, ctitle) {
    let chartDom = document.getElementById('quickstats_radar');
    chartDom.style.width = "340px";
    chartDom.style.height = "250px";
    let myChart = echarts.init(chartDom);
    let categories = [];
    let items = [];
    let max = 0;

    for (let reason in reasons) {
        let xval = 0;
        for (let z = 0; z < details_json.breakdown.length; z++) {
            let word = details_json.breakdown[z][0];
            let val = details_json.breakdown[z][1];
            let xreason = details_json.details.bad_words[word];
            if (xreason === reason) {
                xval += val;
            }
        }
        xval = Math.log2(xval);
        categories.push({name: reason, max: max});
        items.push(xval);
        if (xval > max) max = xval;
    }
    for (let i = 0; i < categories.length; i++) {
        if (categories[i].max > max) max = categories[i].max;
    }
    for (let i = 0; i < categories.length; i++) {
        categories[i].max = max;
    }

    items = items.sort((a,b) => b.value - a.value);
    let options = {
        tooltip: {
            trigger: 'item',
            axisPointer: {            // Use axis to trigger tooltip
                type: 'shadow'        // 'shadow' as default; can also be 'line' or 'shadow'
            },
            formatter: unlog_radar
        },
        title: {
            text: ctitle? ctitle : "Current word breakdown",
            left: 'center'
        },
        radar: {
            // shape: 'circle',
            indicator: categories,
            radius: 65
        },
        series: [{
            name: details_json.repo,
            type: 'radar',
            areaStyle: {},
            data: [
                {
                    value: items,
                    name: details_json.repo
                }
            ]
        }]
    };
    myChart.setOption(options);
}


// Turns those log2 entries back into real numbers
function unlog_radar(params) {
    let i = 0;
    let html = "";
    for (let reason in reasons) {
        let val = 0;
        // log2(0) == -infinity
        if (!isNaN(params.value[i])) {
            val = Math.round(Math.pow(2, params.value[i]));
        }
        html += `<b>${reason}: </b> ${val}<br/>`;
        i++;
    }
    return html
}


function stacked_breakdown(source, chartDom, ctitle = '', legend=true) {
    let x_axis = [];
    let files_processed = [];
    source = source ? source : 'breakdown_timeline';
    for (let z = 1; z < details_json[source][0].length; z++) {
        if (typeof(details_json[source][0][z][0]) == 'number') {
            let d = new Date(details_json[source][0][z][0] * 1000.0);
            x_axis.push(d);
            files_processed.push(details_json[source][0][z][1]);
        }
    }

    let series = [];
    let items = [];
    for (let z = 1; z < details_json[source].length; z++) {
        let item = details_json[source][z];
        let title = item.shift();
        items.push(title);
        let s = {
            name: title,
            type: 'bar',
            stack: 'total',
            emphasis: {
                focus: 'series'
            },
            data: item,
            yAxisIndex: 0
        };
        series.push(s);
    }
    series.push({
        name: "Files processed",
        type: 'line',
        emphasis: {
            focus: 'series'
        },
        data: files_processed,
        yAxisIndex: 1
    })
    let toppx = '32px';
    if (ctitle) toppx = '56px';
    if (legend) {
        toppx = items.length > 5 ? '80px' : '68px';
    }

    chartDom = chartDom ? chartDom : document.getElementById('quickstats');
    chartDom.style.marginBottom = '24px';
    let myChart = echarts.init(chartDom);
    let options = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {            // Use axis to trigger tooltip
                type: 'shadow'        // 'shadow' as default; can also be 'line' or 'shadow'
            }
        },
        title: {
            text: ctitle,
            left: 'center'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: toppx,
            containLabel: true
        },
        toolbox: {
            show: true,
            feature: {
                mark: {show: true},
                dataView: {show: true, readOnly: false},
                restore: {show: true},
                saveAsImage: {show: true},
                magicType: {show: true, type: ['line', 'bar']}
            }
        },
        xAxis: {
            type: 'category',
            data: x_axis,
            axisLabel: {
                formatter: (d) => new Date(d).toDateString()
            }
        },
        yAxis: [{
                type: 'value',
                name: "Word count"
            },
            {
                type: "value",
                name: "Files processed"
            }
            ]
        ,
        series: series
    };
    if (legend) options.legend= {width: '75%', left: 'left', data: items};
    if (ctitle) options.toolbox = null;
    myChart.setOption(options);
}


async function ignore_word(td, tr, repo, word, file, line, column) {
    let rv = await POST('api/ignore.json', {
        repo: repo,
        word: word,
        path: file,
        line: line,
        column: column
    });
    if (rv.okay) {
        tr.style.display = 'none';
        td.parentElement.style.display = 'none';
    } else {
        alert(rv.message);
    }
    return false;
}

async function prime_analysis(limit) {
    document.getElementById('spinner').style.display = 'block';
    document.getElementById('stats').style.display = 'none';
    limit = limit ? limit : 500
    let stats = details_json ? details_json : await GET('/api/details.json' + location.search + "&limit=" + limit);
    details_json = stats;
    document.getElementById('spinner').style.display = 'none';
    document.getElementById('stats').style.display = 'block';

    document.title = `Analysis: ${stats.repo} |  CLC`;
    let n = 0;
    let parent = document.getElementById('quickstats');
    parent.style.width = "720px";
    parent.style.height = "260px";

    repository = stats.repo;
    reasons = stats.reasons;
    stacked_breakdown();
    donut_breakdown();
    radar_breakdown(stats.breakdown, "Context disposition");



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
        let ignore = issue.resolution == 'ignore';
        let tr = document.createElement('tr');
        tr.setAttribute('class', 'table-expand-row');
        tr.setAttribute('data-open-details', "");
        tr.setAttribute('title', "Click to see the context in which this word appears");
        if (ignore) {
            tr.style.background = '#DDD';
            tr.style.color = '#555';
            tr.setAttribute('title', "This occurrence is being ignored by the scanner.");
        }

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
        if (issue.resolution === 'ignore') resolution = 'Ignore word';
        if (issue.resolution === 'intended') resolution = 'Intended word';
        let td_resolution = document.createElement('td');
        td_resolution.innerText = resolution;
        tr.appendChild(td_resolution);
        if (!issue.resolution) {
            tr.style.color = '#900';
        } else {
            tr.style.color = '#080';
        }

        // Actions
        let actions = document.createElement('td');
        if (!ignore) {
            let ibtn = document.createElement('button');
            ibtn.setAttribute('title', "Click to tell CLC to not count this occurrence in its statistics");
            ibtn.setAttribute('class', 'button small');
            ibtn.innerText = "Ignore word";
            ibtn.addEventListener('click', () => ignore_word(actions, tr, stats.repo, issue.word, issue.path, issue.line, issue.mark));
            actions.appendChild(ibtn);
        }
        tr.appendChild(actions);

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

    if (stats.issues.length === limit) {
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
        if (tr.getAttribute('class') === 'table-expand-row-content') continue
        if (txt.length === 0 || tr.innerText.match(re)) {
            tr.style.display = "table-row";
        } else {
            tr.style.display = "none";
        }
    }
}


function analysis_show_stat(which) {
    document.getElementById('quickstats_donut').style.display = 'none';
    document.getElementById('quickstats_radar').style.display = 'none';
    document.getElementById(which).style.display = 'inline-block';
}

function prime_oauth() {
    // pass...
}

// plain login
async function login() {
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    let result = await POST('api/oauth.json', {
        username: username,
        password: password
    });
    if (!result.okay) {
        alert(result.message);
    } else {
        location.href = './'
    }
}

async function logout() {
    let result = await GET('api/preferences?logout=true');
    location.href = location.href;
}

async function prime_prefs() {
    let prefs = await GET('api/preferences.json');
    if (prefs && prefs.login !== null) {
        let lbar = document.getElementById('login');
        lbar.innerHTML = "";

        let alogout = document.createElement('a');
        alogout.setAttribute('href', 'javascript:void(logout());');
        alogout.innerText = "Log out";
        alogout.style.display = "inline-block";
        lbar.appendChild(alogout);

        let welcome = document.createElement('span');
        welcome.setAttribute('class', 'menu-text');
        welcome.innerText = "Welcome, " + prefs.login.name;
        lbar.appendChild(welcome);
    }
}

window.addEventListener('load', prime_prefs);
