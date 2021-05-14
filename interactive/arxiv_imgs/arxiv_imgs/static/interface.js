<script>

function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}

function toggleMode() {
  let checkbox = document.getElementById('search_select');
  console.log("checkbox: " + checkbox.checked)
  let gray = "#cccccc"
  let black = "#000000"
  if(checkbox.checked == 1) {
    document.getElementById("random-text").style.color = gray;
    document.getElementById("embedding-text").style.color = black;
    document.getElementById("image_id_label").style.color = black;
    document.getElementById("embedding").disabled = false;
    document.getElementById("image_id").disabled = false;
  } else if (checkbox.checked == 0) {
    document.getElementById("random-text").style.color = black;
    document.getElementById("embedding-text").style.color = gray;
    document.getElementById("image_id_label").style.color = gray;
    document.getElementById("embedding").disabled = true;
    document.getElementById("image_id").disabled = true;
  }
}

Selectize.define('enter_key_submit', function (options) {
  var self = this;

  this.onKeyDown = (function (e) {
    var original = self.onKeyDown;

    return function (e) {
      // this.items.length MIGHT change after event propagation.
      // We need the initial value as well. See next comment.
      var initialSelection = this.items.length;
      original.apply(this, arguments);

      if (e.keyCode === 13
          // Necessary because we don't want this to be triggered when an option is selected with Enter after pressing DOWN key to trigger the dropdown options
          && initialSelection && initialSelection === this.items.length
          && this.$control_input.val() === '') {
        self.trigger('submit');
      }
    };
  })();
});

$(document).ready(function(){
  const checkbox = document.getElementById('search_select');

  // init Packery
  var $grid = $('.image-grid').packery({
    itemSelector: '.grid-item',
    gutter: 8,
    transitionDuration: 0,
  });
  // layout Packery after each image loads
  $grid.imagesLoaded().progress( function() {
    $grid.packery();
  });

  function show_selected(img_src, img_data, img_prediction) {
    $("#selected_image").css("height", "324px");
    $("#selected-block").css("display", "block");
    let img_src_html = '<img src=' + img_src + ' style="object-fit: contain; max-width: 100%; max-height: 100%;">';
    console.log(img_src_html);
    $("#selected_image").empty().append(img_src_html);
    console.log("prediction: " + img_prediction);
    $('#selected_image').popover('dispose');
    $("#selected_image").popover({
      content: img_prediction,
      title: 'VGG16 prediction',
      html: true,
      trigger: 'hover',
    });

    let checkbox = document.getElementById('search_select');
    if( checkbox.checked == 0) {
      console.log('toggle unchecked, calling toggleMode');
      checkbox.checked = 1;
      toggleMode();
    }

    $("#selected-image-meta").empty().append(img_data);

    $('.si-tab-link').on("click", function (event) {
      console.log("si-tab link clicked");
      let imageID = $(this).attr('image-id');
      let tabID = $(this).attr('id');
      console.log("imageID: " + imageID);
      console.log("tabID: " + tabID);
      let tabSelector = tabID.substring(7, 9);
      console.log("tabSelector: " + tabSelector);
      let targetTabID = "#si-tab-content-" + imageID;
      console.log(targetTabID);
      $( targetTabID ).children().removeClass( "show active" );
      let targetTabContent = '#si-tab-' + imageID + '-' + tabSelector;
      console.log("targetTabContent: " + targetTabContent);
      $( targetTabContent ).addClass( "show active" );
    });

    MathJax.typeset();
  }

  $(".grid-item-img").on("dblclick", function (event) {
    $(this).toggleClass("active");
    $(".grid-item-img").not(this).removeClass("active");
    var img_src = $(this).attr("src");
    var img_id = $(this).parent().attr("image_id");
    // var img_data = $(this).attr("data-content");
    var img_data = $(this).attr("tab-data");
    img_data = img_data.replace(/id='tab-/g, "id='si-tab-");
    img_data = img_data.replace(/tab-link/g, "si-tab-link");

    console.log("img_data: " + img_data);
    var img_pred = $(this).attr("prediction");
    // console.log("showing selected image: " + img_src);
    show_selected(img_src, img_data, img_pred);

    console.log("setting image_id to: " + img_id);
    console.log("prediction: " + img_pred);
    $("#image_id").val(img_id);
    $(".results").empty().append(img_id);
  });

  $(".grid-item-img").on("click", function (event) {
    console.log('disposing popovers');
    $(".grid-item-img").not(this).popover('dispose');
    console.log('creating popover');
    console.log(this);
    let imgDiv = '<img class="popover-image" src="' + $(this).attr('src') + '">';
    let tabData = $(this).attr('tab-data');
    let popoverData = imgDiv + tabData;
    console.log("popoverData: " + popoverData);
    $(this).popover({
      html: true,
      trigger: 'manual',
      title: "Image Metadata",
      sanitize: false,
      // selector: '[rel=selector]',
      // placement: "bottom",
      content: popoverData,
    });

    $(".grid-item-img").not(this).popover('hide');
    $(this).popover('show');

    $('.tab-link').on("click", function (event) {
      console.log("link clicked");
      let imageID = $(this).attr('image-id');
      let tabID = $(this).attr('id');
      console.log("imageID: " + imageID);
      console.log("tabID: " + tabID);
      let tabSelector = tabID.substring(4, 6);
      console.log("tabSelector: " + tabSelector);
      let targetTabID = "#tab-content-" + imageID;
      console.log(targetTabID);
      $( targetTabID ).children().removeClass( "show active" );
      let targetTabContent = '#tab-' + imageID + '-' + tabSelector;
      console.log("targetTabContent: " + targetTabContent);
      $( targetTabContent ).addClass( "show active" );
    });
  })

  {% if prev_image_id %}
    console.log("prev_image_id not empty: " + {{ prev_image_id }});
    var img_src = {{url_for("static", filename="all/"+prev_image_id+".jpg")|tojson}};
    {% if si_meta[8]|length > 100 %}
      {% set si_authors_short = si_meta[8].split(";")[0] + " et al" %}
    {% else %}
      {% set si_authors_short = si_meta[8] %}
    {% endif %}
    {% if si_meta[11] != "None" %}
      {% set si_caption = si_meta[11] %}
    {% else %}
      {% set si_caption = "-" %}
    {% endif %}
    {% set pl = si_meta[10].lower().replace(","," ").split() %}
    {% set si_prediction_formatted = "{} {}<br>{} {}<br>{} {}<br>{} {}<br>{} {}".format(pl[1], pl[0], pl[3], pl[2], pl[5], pl[4], pl[7], pl[6], pl[9], pl[8]) %}
    var img_pred = '{% autoescape false %} {{ si_prediction_formatted }} {% endautoescape %}';
    var img_data = {{"<div class='meta-col'><b><em>Image</em><br>filename:</b> {}<br><b>x:</b> {}<b> y:</b> {}<br><b>format:</b> {}<br><b>creator:</b> {}<br><br></div><div class='meta-col'><b><em>Paper</em><br>identifier:</b> <a href=https://arxiv.org/abs/{}>{}</a><br><b>date:</b> {}<br><b>category:</b> {}<br><b>authors:</b> {}<br><b>title:</b> {}<br><br></div><div class='meta-col'><b><em>Figure</em><br>caption:</b> {}".format(si_meta[1], si_meta[2], si_meta[3], si_meta[4], si_meta[5], si_meta[0], si_meta[0], si_meta[6], si_meta[7], si_authors_short, si_meta[9], si_caption)|tojson }};
    // console.log(img_data);

    show_selected(img_src, img_data, img_pred);
  {% else %}
    $("#selected-block").css("display", "none");
  {% endif %}

  var $select = $('#author').selectize({
    delimiter: ',',
    persist: false,
    maxItems: 1,
    plugins: ['remove_button', 'enter_key_submit'],
    onInitialize: function () {
      this.on('submit', function () {
        this.$input.closest('form').submit();
      }, this);
    },
    valueField: 'cat',
    labelField: 'label',
    searchField: ['cat', 'label'],
    options: [
      {'cat': 'Wang', 'label': '3778'}, {'cat': 'Li', 'label': '3408'}, {'cat': 'Zhang', 'label': '3248'}, {'cat': 'Chen', 'label': '2819'}, {'cat': 'Liu', 'label': '2580'}, {'cat': 'Yang', 'label': '1456'}, {'cat': 'Lee', 'label': '1370'}, {'cat': 'Kim', 'label': '1203'}, {'cat': 'Wu', 'label': '1165'}, {'cat': 'Xu', 'label': '1125'}, {'cat': 'Huang', 'label': '1105'}, {'cat': 'Zhao', 'label': '859'}, {'cat': 'Zhou', 'label': '858'}, {'cat': 'Lin', 'label': '758'}, {'cat': 'Zhu', 'label': '731'}, {'cat': 'Yu', 'label': '730'}, {'cat': 'Sun', 'label': '701'}, {'cat': 'Hu', 'label': '638'}, {'cat': 'Guo', 'label': '626'}, {'cat': 'Jiang', 'label': '607'}, {'cat': 'Ma', 'label': '601'}, {'cat': 'Lu', 'label': '581'}, {'cat': 'He', 'label': '580'}, {'cat': 'Kumar', 'label': '542'}, {'cat': 'ATLAS Collaboration', 'label': '527'}, {'cat': 'CMS Collaboration', 'label': '525'}, {'cat': 'Singh', 'label': '515'}, {'cat': 'Gao', 'label': '508'}, {'cat': 'Park', 'label': '459'}, {'cat': 'Chang', 'label': '438'}, {'cat': 'Das', 'label': '435'}, {'cat': 'Song', 'label': '429'}, {'cat': 'Feng', 'label': '428'}, {'cat': 'Nguyen', 'label': '420'}, {'cat': 'Cheng', 'label': '409'}, {'cat': 'Han', 'label': '409'}, {'cat': 'Cao', 'label': '408'}, {'cat': 'Shi', 'label': '404'}, {'cat': 'Gupta', 'label': '397'}, {'cat': 'Tang', 'label': '395'}, {'cat': 'Zheng', 'label': '392'}, {'cat': 'Yan', 'label': '384'}, {'cat': 'Luo', 'label': '381'}, {'cat': 'Ghosh', 'label': '379'}, {'cat': 'Smith', 'label': '375'}, {'cat': 'Shen', 'label': '373'}, {'cat': 'Cai', 'label': '365'}, {'cat': 'Choi', 'label': '352'}, {'cat': 'Jin', 'label': '331'}, {'cat': 'Xie', 'label': '330'}, {'cat': 'Yuan', 'label': '316'}, {'cat': 'Ding', 'label': '310'}, {'cat': 'Dong', 'label': '310'}, {'cat': 'Fan', 'label': '307'}, {'cat': 'Martin', 'label': '290'}, {'cat': 'Sharma', 'label': '287'}, {'cat': 'Xiao', 'label': '282'}, {'cat': 'Roy', 'label': '278'}, {'cat': 'Liang', 'label': '274'}, {'cat': 'Wei', 'label': '273'}, {'cat': 'Fu', 'label': '268'}, {'cat': 'Pan', 'label': '266'}, {'cat': 'Banerjee', 'label': '264'}, {'cat': 'Cohen', 'label': '253'}, {'cat': 'Brown', 'label': '252'}, {'cat': 'Collaboration', 'label': '249'}, {'cat': 'Kang', 'label': '249'}, {'cat': 'Dai', 'label': '246'}, {'cat': 'Fang', 'label': '244'}, {'cat': 'Peng', 'label': '244'}, {'cat': 'Miller', 'label': '241'}, {'cat': 'Yao', 'label': '237'}, {'cat': 'Deng', 'label': '236'}, {'cat': 'Johnson', 'label': '234'}, {'cat': 'Schmidt', 'label': '228'}, {'cat': 'Du', 'label': '227'}, {'cat': 'Anderson', 'label': '226'}, {'cat': 'Cho', 'label': '226'}, {'cat': 'Cui', 'label': '222'}, {'cat': 'LHCb collaboration', 'label': '217'}, {'cat': 'Hong', 'label': '215'}, {'cat': 'Jones', 'label': '214'}, {'cat': 'Williams', 'label': '214'}, {'cat': 'Tan', 'label': '213'}, {'cat': 'Ye', 'label': '213'}, {'cat': 'Ellis', 'label': '212'}, {'cat': 'Gu', 'label': '211'}, {'cat': 'Gong', 'label': '207'}, {'cat': 'Jain', 'label': '204'}, {'cat': 'Hou', 'label': '203'}, {'cat': 'Santos', 'label': '203'}, {'cat': 'Bhattacharya', 'label': '200'}, {'cat': 'Ren', 'label': '199'}, {'cat': 'Jia', 'label': '198'}, {'cat': 'Chakraborty', 'label': '194'}, {'cat': 'Zeng', 'label': '192'}, {'cat': 'Liao', 'label': '191'}, {'cat': 'Mukherjee', 'label': '190'}, {'cat': 'Su', 'label': '190'}, {'cat': 'Dutta', 'label': '189'}, {'cat': 'Evans', 'label': '188'}, {'cat': 'Yin', 'label': '188'}, {'cat': 'Tanaka', 'label': '178'}, {'cat': 'Ivanov', 'label': '176'}, {'cat': 'Khan', 'label': '176'}, {'cat': 'Chan', 'label': '172'}, {'cat': 'Qin', 'label': '172'}, {'cat': 'Tran', 'label': '172'}, {'cat': 'Wen', 'label': '172'}, {'cat': 'Thomas', 'label': '171'}, {'cat': 'Tian', 'label': '169'}, {'cat': 'The BABAR Collaboration', 'label': '168'}, {'cat': 'Bauer', 'label': '164'}, {'cat': 'Costa', 'label': '163'}, {'cat': 'ALICE Collaboration', 'label': '162'}, {'cat': 'Ali', 'label': '162'}, {'cat': 'Aoki', 'label': '162'}, {'cat': 'Bai', 'label': '162'}, {'cat': 'Chatterjee', 'label': '162'}, {'cat': 'Ji', 'label': '161'}, {'cat': 'Mishra', 'label': '161'}, {'cat': 'Schneider', 'label': '161'}, {'cat': 'Ahmed', 'label': '160'}, {'cat': 'Biswas', 'label': '160'}, {'cat': 'Müller', 'label': '159'}, {'cat': 'Jung', 'label': '156'}, {'cat': 'Zhong', 'label': '155'}, {'cat': 'Berger', 'label': '154'}, {'cat': 'Ho', 'label': '153'}, {'cat': 'Taylor', 'label': '152'}, {'cat': 'Chung', 'label': '151'}, {'cat': 'Fischer', 'label': '151'}, {'cat': 'Sarkar', 'label': '150'}, {'cat': 'Lim', 'label': '149'}, {'cat': 'Takahashi', 'label': '149'}, {'cat': 'Kobayashi', 'label': '148'}, {'cat': 'Qian', 'label': '148'}, {'cat': 'Saha', 'label': '148'}, {'cat': 'Suzuki', 'label': '148'}, {'cat': 'Agarwal', 'label': '147'}, {'cat': 'Meng', 'label': '147'}, {'cat': 'Wong', 'label': '147'}, {'cat': 'Nakamura', 'label': '146'}, {'cat': 'Lai', 'label': '145'}, {'cat': 'Abe', 'label': '142'}, {'cat': 'Xue', 'label': '142'}, {'cat': 'Zou', 'label': '142'}, {'cat': 'Silva', 'label': '141'}, {'cat': 'White', 'label': '141'}, {'cat': 'Meyer', 'label': '140'}, {'cat': 'Shao', 'label': '139'}, {'cat': 'Xia', 'label': '139'}, {'cat': 'Xiong', 'label': '139'}, {'cat': 'Mao', 'label': '138'}, {'cat': 'Qi', 'label': '137'}, {'cat': 'Pal', 'label': '136'}, {'cat': 'Qiu', 'label': '136'}, {'cat': 'Dey', 'label': '135'}, {'cat': 'Sato', 'label': '135'}, {'cat': 'Gonzalez', 'label': '134'}, {'cat': 'Joshi', 'label': '132'}, {'cat': 'Wilson', 'label': '129'}, {'cat': 'Braun', 'label': '128'}, {'cat': 'Ge', 'label': '128'}, {'cat': 'Yoshida', 'label': '128'}, {'cat': 'Clark', 'label': '127'}, {'cat': 'Garcia', 'label': '127'}, {'cat': 'Davis', 'label': '126'}, {'cat': 'Becker', 'label': '124'}, {'cat': 'Klein', 'label': '124'}, {'cat': 'Kato', 'label': '123'}, {'cat': 'Pandey', 'label': '123'}, {'cat': 'Ferreira', 'label': '122'}, {'cat': 'Le', 'label': '122'}, {'cat': 'Andersen', 'label': '121'}, {'cat': 'Choudhury', 'label': '121'}, {'cat': 'Bao', 'label': '119'}, {'cat': 'Hansen', 'label': '118'}, {'cat': 'Hoang', 'label': '118'}, {'cat': 'Watanabe', 'label': '118'}, {'cat': 'Chu', 'label': '117'}, {'cat': 'Hwang', 'label': '117'}, {'cat': 'Yamamoto', 'label': '117'}, {'cat': 'D0 Collaboration', 'label': '116'}, {'cat': 'Lei', 'label': '116'}, {'cat': 'Paul', 'label': '116'}, {'cat': 'Harris', 'label': '115'}, {'cat': 'Kong', 'label': '115'}, {'cat': 'Torres', 'label': '115'}, {'cat': 'Wan', 'label': '115'}, {'cat': 'Simon', 'label': '114'}, {'cat': 'Basu', 'label': '113'}, {'cat': 'King', 'label': '112'}, {'cat': 'Adams', 'label': '111'}, {'cat': 'Oh', 'label': '111'}, {'cat': 'Planck Collaboration', 'label': '111'}, {'cat': 'Rahman', 'label': '111'}, {'cat': 'Rao', 'label': '111'}, {'cat': 'You', 'label': '111'}, {'cat': 'Cheung', 'label': '110'}, {'cat': 'Yi', 'label': '110'}, {'cat': 'Chowdhury', 'label': '109'}, {'cat': 'Green', 'label': '108'}, {'cat': 'Roberts', 'label': '108'}, {'cat': 'Shah', 'label': '108'}, {'cat': 'Shin', 'label': '108'}, {'cat': 'Inoue', 'label': '107'}, {'cat': 'Srivastava', 'label': '107'}, {'cat': 'An', 'label': '106'}, {'cat': 'Mueller', 'label': '106'}, {'cat': 'Davies', 'label': '105'}, {'cat': 'Rodriguez', 'label': '105'}, {'cat': 'Bhattacharyya', 'label': '104'}, {'cat': 'Perez', 'label': '104'}, {'cat': 'Brandt', 'label': '103'}, {'cat': 'Hao', 'label': '103'}, {'cat': 'Hashimoto', 'label': '103'}, {'cat': 'Weber', 'label': '103'}, {'cat': 'Almeida', 'label': '102'}, {'cat': 'Baker', 'label': '102'}, {'cat': 'Barnes', 'label': '102'}, {'cat': 'Islam', 'label': '102'}, {'cat': 'Ahn', 'label': '101'}, {'cat': 'Beck', 'label': '101'}, {'cat': 'Hall', 'label': '101'}, {'cat': 'Hsu', 'label': '101'}, {'cat': 'Oliveira', 'label': '101'}, {'cat': 'Werner', 'label': '101'}, {'cat': 'da Silva', 'label': '101'}, {'cat': 'Chakrabarti', 'label': '100'}, {'cat': 'Huber', 'label': '100'}, {'cat': 'Long', 'label': '100'}, {'cat': 'Young', 'label': '100'}, {'cat': 'Bianchi', 'label': '99'}, {'cat': 'Rodrigues', 'label': '98'}, {'cat': 'ZEUS Collaboration', 'label': '98'}, {'cat': 'Arnold', 'label': '97'}, {'cat': 'Campbell', 'label': '97'}, {'cat': 'Sinha', 'label': '97'}, {'cat': 'Bell', 'label': '96'}, {'cat': 'Xiang', 'label': '96'}, {'cat': 'Duan', 'label': '95'}, {'cat': 'Ribeiro', 'label': '95'}, {'cat': 'Rossi', 'label': '95'}, {'cat': 'Wright', 'label': '95'}, {'cat': 'Yoon', 'label': '95'}, {'cat': 'CDF Collaboration', 'label': '93'}, {'cat': 'Datta', 'label': '93'}, {'cat': 'Mandal', 'label': '93'}, {'cat': 'Saito', 'label': '93'}
    ],
    render: {
      item: function(item, escape) {
          return '<div>' +
              (item.cat ? '<span class="cat">' + escape(item.cat) + ' - </span>' : '') +
              (item.label ? '<span class="label">' + escape(item.label) + '</span>' : '') +
          '</div>';
      },
      option: function(item, escape) {
          var label = item.cat || item.label;
          var caption = item.cat ? item.label : null;
          return '<div>' +
              '<span class="label">' + escape(label) + ' - </span>' +
              (caption ? '<span class="caption">' + escape(caption) + '</span>' : '') +
          '</div>';
      }
    },
    create: function(input) {
        return {
            cat: input,
            label: input
        }
    }
  });
  var authorSelect = $select[0].selectize;

  var $select = $('#prediction').selectize({
    delimiter: ',',
    persist: false,
    maxItems: 1,
    plugins: ['remove_button', 'enter_key_submit'],
    onInitialize: function () {
      this.on('submit', function () {
        this.$input.closest('form').submit();
      }, this);
    },
    valueField: 'cat',
    labelField: 'label',
    searchField: ['cat', 'label'],
    options: [
      {'cat': 'oscilloscope', 'label': '86013'}, {'cat': 'web_site', 'label': '78592'}, {'cat': 'rule', 'label': '62818'}, {'cat': 'slide_rule', 'label': '53678'}, {'cat': 'envelope', 'label': '44853'}, {'cat': 'menu', 'label': '33113'}, {'cat': 'bow', 'label': '18544'}, {'cat': 'nematode', 'label': '14257'}, {'cat': 'crane', 'label': '14243'}, {'cat': 'binder', 'label': '11379'}, {'cat': 'spider_web', 'label': '8914'}, {'cat': 'maze', 'label': '7299'}, {'cat': 'crossword_puzzle', 'label': '6993'}, {'cat': 'swing', 'label': '6722'}, {'cat': 'hook', 'label': '6273'}, {'cat': 'jigsaw_puzzle', 'label': '5996'}, {'cat': 'wall_clock', 'label': '5708'}, {'cat': 'analog_clock', 'label': '4913'}, {'cat': 'stupa', 'label': '3418'}, {'cat': 'necklace', 'label': '3414'}, {'cat': 'scale', 'label': '3238'}, {'cat': 'syringe', 'label': '3044'}, {'cat': 'chime', 'label': '3002'}, {'cat': 'screwdriver', 'label': '2922'}, {'cat': 'shower_curtain', 'label': '2425'}, {'cat': 'pole', 'label': '2362'}, {'cat': 'magnetic_compass', 'label': '2209'}, {'cat': 'tripod', 'label': '2134'}, {'cat': 'traffic_light', 'label': '1975'}, {'cat': 'window_screen', 'label': '1830'}, {'cat': 'digital_clock', 'label': '1787'}, {'cat': 'nail', 'label': '1743'}, {'cat': 'whistle', 'label': '1554'}, {'cat': 'switch', 'label': '1465'}, {'cat': 'chain', 'label': '1431'}, {'cat': 'bubble', 'label': '1304'}, {'cat': 'fountain', 'label': '1287'}, {'cat': 'picket_fence', 'label': '1255'}, {'cat': 'safety_pin', 'label': '1249'}, {'cat': 'gong', 'label': '1120'}, {'cat': 'parachute', 'label': '1075'}, {'cat': 'harvestman', 'label': '1058'}, {'cat': 'matchstick', 'label': '1057'}, {'cat': 'handkerchief', 'label': '1050'}, {'cat': 'book_jacket', 'label': '1023'}, {'cat': 'jellyfish', 'label': '999'}, {'cat': 'rubber_eraser', 'label': '908'}, {'cat': 'spotlight', 'label': '887'}, {'cat': 'abacus', 'label': '885'}, {'cat': 'chainlink_fence', 'label': '876'}, {'cat': 'solar_dish', 'label': '855'}, {'cat': 'pinwheel', 'label': '814'}, {'cat': 'scoreboard', 'label': '813'}, {'cat': 'microphone', 'label': '782'}, {'cat': 'hair_slide', 'label': '756'}, {'cat': 'balloon', 'label': '748'}, {'cat': 'coil', 'label': '724'}, {'cat': 'cleaver', 'label': '722'}, {'cat': 'pick', 'label': '720'}, {'cat': 'wardrobe', 'label': '714'}, {'cat': 'plate_rack', 'label': '694'}, {'cat': 'honeycomb', 'label': '689'}, {'cat': 'screw', 'label': '646'}, {'cat': 'ski', 'label': '620'}, {'cat': 'window_shade', 'label': '601'}, {'cat': 'corkscrew', 'label': '600'}, {'cat': 'fountain_pen', 'label': '592'}, {'cat': 'maypole', 'label': '582'}, {'cat': 'monitor', 'label': '576'}, {'cat': 'walking_stick', 'label': '576'}, {'cat': 'umbrella', 'label': '574'}, {'cat': 'candle', 'label': '570'}, {'cat': 'bow_tie', 'label': '541'}, {'cat': 'bib', 'label': '534'}, {'cat': 'pirate', 'label': '530'}, {'cat': 'horizontal_bar', 'label': '509'}, {'cat': 'prayer_rug', 'label': '489'}, {'cat': 'flagpole', 'label': '483'}, {'cat': 'oboe', 'label': '480'}, {'cat': 'suit', 'label': '479'}, {'cat': 'swab', 'label': '471'}, {'cat': 'power_drill', 'label': '448'}, {'cat': 'ballpoint', 'label': '447'}, {'cat': 'volcano', 'label': '426'}, {'cat': 'wig', 'label': '426'}, {'cat': 'sliding_door', 'label': '425'}, {'cat': 'measuring_cup', 'label': '416'}, {'cat': 'fire_screen', 'label': '407'}, {'cat': 'jersey', 'label': '407'}, {'cat': 'Band_Aid', 'label': '401'}, {'cat': 'radio_telescope', 'label': '394'}, {'cat': 'prison', 'label': '387'}, {'cat': 'mouse', 'label': '384'}, {'cat': 'shoji', 'label': '383'}, {'cat': 'street_sign', 'label': '381'}, {'cat': 'brassiere', 'label': '379'}, {'cat': 'Windsor_tie', 'label': '372'}, {'cat': 'container_ship', 'label': '372'}, {'cat': 'carton', 'label': '363'}, {'cat': 'mask', 'label': '359'}, {'cat': 'puck', 'label': '358'}, {'cat': 'quill', 'label': '350'}, {'cat': 'electric_fan', 'label': '348'}, {'cat': 'bell_cote', 'label': '342'}, {'cat': 'doormat', 'label': '342'}, {'cat': 'iPod', 'label': '342'}, {'cat': 'sombrero', 'label': '337'}, {'cat': 'bee_eater', 'label': '335'}, {'cat': 'sundial', 'label': '334'}, {'cat': 'remote_control', 'label': '324'}, {'cat': 'Petri_dish', 'label': '322'}, {'cat': 'airship', 'label': '322'}, {'cat': 'pencil_sharpener', 'label': '311'}, {'cat': 'tray', 'label': '311'}, {'cat': 'lampshade', 'label': '309'}, {'cat': 'rifle', 'label': '302'}, {'cat': 'toilet_seat', 'label': '298'}, {'cat': 'stage', 'label': '297'}, {'cat': 'red_wine', 'label': '294'}, {'cat': 'loupe', 'label': '293'}, {'cat': 'loudspeaker', 'label': '292'}, {'cat': 'croquet_ball', 'label': '290'}, {'cat': 'folding_chair', 'label': '287'}, {'cat': 'ping-pong_ball', 'label': '285'}, {'cat': 'seashore', 'label': '280'}, {'cat': 'mortarboard', 'label': '278'}, {'cat': 'cricket', 'label': '276'}, {'cat': 'lacewing', 'label': '270'}, {'cat': 'wallet', 'label': '266'}, {'cat': 'bolo_tie', 'label': '265'}, {'cat': 'slot', 'label': '264'}, {'cat': 'stole', 'label': '260'}, {'cat': 'suspension_bridge', 'label': '258'}, {'cat': 'warplane', 'label': '256'}, {'cat': 'strainer', 'label': '254'}, {'cat': 'bathing_cap', 'label': '253'}, {'cat': 'face_powder', 'label': '252'}, {'cat': 'lighter', 'label': '249'}, {'cat': 'modem', 'label': '249'}, {'cat': 'cassette', 'label': '245'}, {'cat': 'stethoscope', 'label': '244'}, {'cat': 'poncho', 'label': '243'}, {'cat': 'dishrag', 'label': '242'}, {'cat': 'screen', 'label': '237'}, {'cat': 'pillow', 'label': '236'}, {'cat': 'streetcar', 'label': '236'}, {'cat': 'theater_curtain', 'label': '231'}, {'cat': 'shoe_shop', 'label': '228'}, {'cat': 'stopwatch', 'label': '226'}, {'cat': 'clog', 'label': '219'}, {'cat': 'ant', 'label': '218'}, {'cat': 'lipstick', 'label': '218'}, {'cat': 'long-horned_beetle', 'label': '218'}, {'cat': 'comic_book', 'label': '213'}, {'cat': 'punching_bag', 'label': '213'}, {'cat': 'paper_towel', 'label': '211'}, {'cat': 'radiator', 'label': '210'}, {'cat': 'tennis_ball', 'label': '205'}, {'cat': 'velvet', 'label': '205'}, {'cat': 'desk', 'label': '202'}, {'cat': 'knot', 'label': '199'}, {'cat': 'bonnet', 'label': '198'}, {'cat': 'castle', 'label': '198'}, {'cat': 'shield', 'label': '198'}, {'cat': 'iron', 'label': '196'}, {'cat': 'harp', 'label': '194'}, {'cat': 'shower_cap', 'label': '194'}, {'cat': 'chain_mail', 'label': '185'}, {'cat': 'torch', 'label': '181'}, {'cat': 'golf_ball', 'label': '179'}, {'cat': 'padlock', 'label': '176'}, {'cat': 'toyshop', 'label': '173'}, {'cat': 'computer_keyboard', 'label': '172'}, {'cat': 'lab_coat', 'label': '166'}, {'cat': 'pencil_box', 'label': '166'}, {'cat': 'pug', 'label': '166'}, {'cat': 'soccer_ball', 'label': '165'}, {'cat': 'refrigerator', 'label': '164'}, {'cat': 'file', 'label': '162'}, {'cat': 'lakeside', 'label': '160'}, {'cat': 'paintbrush', 'label': '158'}, {'cat': 'tiger_beetle', 'label': '158'}, {'cat': 'palace', 'label': '156'}, {'cat': 'schooner', 'label': '155'}, {'cat': 'turnstile', 'label': '154'}, {'cat': 'letter_opener', 'label': '153'}, {'cat': 'sock', 'label': '153'}, {'cat': 'fireboat', 'label': '151'}, {'cat': 'television', 'label': '150'}, {'cat': 'washbasin', 'label': '150'}, {'cat': 'wool', 'label': '147'}, {'cat': 'apron', 'label': '145'}, {'cat': 'library', 'label': '145'}, {'cat': 'dumbbell', 'label': '144'}, {'cat': 'maraca', 'label': '144'}, {'cat': 'cockroach', 'label': '141'}, {'cat': 'sea_urchin', 'label': '141'}, {'cat': 'vase', 'label': '140'}, {'cat': 'barbell', 'label': '139'}, {'cat': "jack-o'-lantern", 'label': '138'}, {'cat': 'parallel_bars', 'label': '138'}, {'cat': 'wine_bottle', 'label': '137'}, {'cat': 'brass', 'label': '136'}, {'cat': 'tick', 'label': '135'}, {'cat': 'cinema', 'label': '134'}, {'cat': 'racket', 'label': '133'}, {'cat': 'geyser', 'label': '132'}, {'cat': 'church', 'label': '131'}, {'cat': 'packet', 'label': '131'}, {'cat': 'bucket', 'label': '129'}, {'cat': 'starfish', 'label': '129'}, {'cat': 'garbage_truck', 'label': '126'}, {'cat': 'space_shuttle', 'label': '126'}, {'cat': 'broom', 'label': '124'}, {'cat': 'sarong', 'label': '124'}, {'cat': 'bannister', 'label': '123'}, {'cat': 'cash_machine', 'label': '122'}, {'cat': 'shopping_basket', 'label': '121'}, {'cat': 'liner', 'label': '118'}, {'cat': 'bottlecap', 'label': '117'}, {'cat': 'manhole_cover', 'label': '117'}, {'cat': 'alp', 'label': '116'}, {'cat': 'centipede', 'label': '116'}, {'cat': 'hourglass', 'label': '116'}, {'cat': 'perfume', 'label': '116'}, {'cat': 'dam', 'label': '115'}, {'cat': 'toilet_tissue', 'label': '115'}, {'cat': 'neck_brace', 'label': '114'}, {'cat': 'washer', 'label': '114'}, {'cat': 'bassoon', 'label': '113'}, {'cat': 'birdhouse', 'label': '113'}, {'cat': 'balance_beam', 'label': '112'}, {'cat': 'conch', 'label': '111'}, {'cat': 'sweatshirt', 'label': '111'}, {'cat': 'mitten', 'label': '109'}, {'cat': 'safe', 'label': '109'}, {'cat': 'cliff', 'label': '108'}, {'cat': 'fur_coat', 'label': '107'}, {'cat': 'laptop', 'label': '107'}, {'cat': 'vending_machine', 'label': '107'}, {'cat': 'beacon', 'label': '106'}, {'cat': 'beaker', 'label': '106'}, {'cat': 'electric_guitar', 'label': '105'}, {'cat': 'space_heater', 'label': '105'}, {'cat': 'sunglasses', 'label': '103'}, {'cat': 'vault', 'label': '102'}, {'cat': 'abaya', 'label': '100'}, {'cat': 'pay-phone', 'label': '100'}, {'cat': 'pier', 'label': '100'}, {'cat': 'dragonfly', 'label': '99'}
    ],
    render: {
      item: function(item, escape) {
          return '<div>' +
              (item.cat ? '<span class="cat">' + escape(item.cat) + ' - </span>' : '') +
              (item.label ? '<span class="label">' + escape(item.label) + '</span>' : '') +
          '</div>';
      },
      option: function(item, escape) {
          var label = item.cat || item.label;
          var caption = item.cat ? item.label : null;
          return '<div>' +
              '<span class="label">' + escape(label) + ' - </span>' +
              (caption ? '<span class="caption">' + escape(caption) + '</span>' : '') +
          '</div>';
      }
    },
    create: function(input) {
        return {
            cat: input,
            label: input
        }
    }
  });
  var predictionSelect = $select[0].selectize;

  var $select = $('#category').selectize({
      delimiter: ',',
      persist: false,
      maxItems: 1,
      plugins: ['remove_button', 'enter_key_submit'],
      onInitialize: function () {
        this.on('submit', function () {
          this.$input.closest('form').submit();
        }, this);
      },
      valueField: 'cat',
      labelField: 'label',
      searchField: ['cat', 'label'],
      options: [
        {'cat': 'astro-ph.GA', 'label': 'Astrophysics of Galaxies'}, {'cat': 'astro-ph.CO', 'label': 'Cosmology and Nongalactic Astrophysics'}, {'cat': 'astro-ph.EP', 'label': 'Earth and Planetary Astrophysics'}, {'cat': 'astro-ph.HE', 'label': 'High Energy Astrophysical Phenomena'}, {'cat': 'astro-ph.IM', 'label': 'Instrumentation and Methods for Astrophysics'}, {'cat': 'astro-ph.SR', 'label': 'Solar and Stellar Astrophysics'}, {'cat': 'cond-mat.dis-nn', 'label': 'Disordered Systems and Neural Networks'}, {'cat': 'cond-mat.mtrl-sci', 'label': 'Materials Science'}, {'cat': 'cond-mat.mes-hall', 'label': 'Mesoscale and Nanoscale Physics'}, {'cat': 'cond-mat.other', 'label': 'Other Condensed Matter'}, {'cat': 'cond-mat.quant-gas', 'label': 'Quantum Gases'}, {'cat': 'cond-mat.soft', 'label': 'Soft Condensed Matter'}, {'cat': 'cond-mat.stat-mech', 'label': 'Statistical Mechanics'}, {'cat': 'cond-mat.str-el', 'label': 'Strongly Correlated Electrons'}, {'cat': 'cond-mat.supr-con', 'label': 'Superconductivity'}, {'cat': 'gr-qc', 'label': 'General Relativity and Quantum Cosmology'}, {'cat': 'hep-ex', 'label': 'High Energy Physics - Experiment'}, {'cat': 'hep-lat', 'label': 'High Energy Physics - Lattice'}, {'cat': 'hep-ph', 'label': 'High Energy Physics - Phenomenology'}, {'cat': 'hep-th', 'label': 'High Energy Physics - Theory'}, {'cat': 'math-ph', 'label': 'Mathematical Physics'}, {'cat': 'nlin.AO', 'label': 'Adaptation and Self-Organizing Systems'}, {'cat': 'nlin.CG', 'label': 'Cellular Automata and Lattice Gases'}, {'cat': 'nlin.CD', 'label': 'Chaotic Dynamics'}, {'cat': 'nlin.SI', 'label': 'Exactly Solvable and Integrable Systems'}, {'cat': 'nlin.PS', 'label': 'Pattern Formation and Solitons'}, {'cat': 'nucl-ex', 'label': 'Nuclear Experiment'}, {'cat': 'nucl-th', 'label': 'Nuclear Theory'}, {'cat': 'physics.acc-ph', 'label': 'Accelerator Physics'}, {'cat': 'physics.app-ph', 'label': 'Applied Physics'}, {'cat': 'physics.ao-ph', 'label': 'Atmospheric and Oceanic Physics'}, {'cat': 'physics.atom-ph', 'label': 'Atomic Physics'}, {'cat': 'physics.atm-clus', 'label': 'Atomic and Molecular Clusters'}, {'cat': 'physics.bio-ph', 'label': 'Biological Physics'}, {'cat': 'physics.chem-ph', 'label': 'Chemical Physics'}, {'cat': 'physics.class-ph', 'label': 'Classical Physics'}, {'cat': 'physics.comp-ph', 'label': 'Computational Physics'}, {'cat': 'physics.data-an', 'label': 'Data Analysis, Statistics and Probability'}, {'cat': 'physics.flu-dyn', 'label': 'Fluid Dynamics'}, {'cat': 'physics.gen-ph', 'label': 'General Physics'}, {'cat': 'physics.geo-ph', 'label': 'Geophysics'}, {'cat': 'physics.hist-ph', 'label': 'History and Philosophy of Physics'}, {'cat': 'physics.ins-det', 'label': 'Instrumentation and Detectors'}, {'cat': 'physics.med-ph', 'label': 'Medical Physics'}, {'cat': 'physics.optics', 'label': 'Optics'}, {'cat': 'physics.ed-ph', 'label': 'Physics Education'}, {'cat': 'physics.soc-ph', 'label': 'Physics and Society'}, {'cat': 'physics.plasm-ph', 'label': 'Plasma Physics'}, {'cat': 'physics.pop-ph', 'label': 'Popular Physics'}, {'cat': 'physics.space-ph', 'label': 'Space Physics'}, {'cat': 'quant-ph', 'label': 'Quantum Physics'}, {'cat': 'math.AG', 'label': 'Algebraic Geometry'}, {'cat': 'math.AT', 'label': 'Algebraic Topology'}, {'cat': 'math.AP', 'label': 'Analysis of PDEs'}, {'cat': 'math.CT', 'label': 'Category Theory'}, {'cat': 'math.CA', 'label': 'Classical Analysis and ODEs'}, {'cat': 'math.CO', 'label': 'Combinatorics'}, {'cat': 'math.AC', 'label': 'Commutative Algebra'}, {'cat': 'math.CV', 'label': 'Complex Variables'}, {'cat': 'math.DG', 'label': 'Differential Geometry'}, {'cat': 'math.DS', 'label': 'Dynamical Systems'}, {'cat': 'math.FA', 'label': 'Functional Analysis'}, {'cat': 'math.GM', 'label': 'General Mathematics'}, {'cat': 'math.GN', 'label': 'General Topology'}, {'cat': 'math.GT', 'label': 'Geometric Topology'}, {'cat': 'math.GR', 'label': 'Group Theory'}, {'cat': 'math.HO', 'label': 'History and Overview'}, {'cat': 'math.IT', 'label': 'Information Theory'}, {'cat': 'math.KT', 'label': 'K-Theory and Homology'}, {'cat': 'math.LO', 'label': 'Logic'}, {'cat': 'math.MP', 'label': 'Mathematical Physics'}, {'cat': 'math.MG', 'label': 'Metric Geometry'}, {'cat': 'math.NT', 'label': 'Number Theory'}, {'cat': 'math.NA', 'label': 'Numerical Analysis'}, {'cat': 'math.OA', 'label': 'Operator Algebras'}, {'cat': 'math.OC', 'label': 'Optimization and Control'}, {'cat': 'math.PR', 'label': 'Probability'}, {'cat': 'math.QA', 'label': 'Quantum Algebra'}, {'cat': 'math.RT', 'label': 'Representation Theory'}, {'cat': 'math.RA', 'label': 'Rings and Algebras'}, {'cat': 'math.SP', 'label': 'Spectral Theory'}, {'cat': 'math.ST', 'label': 'Statistics Theory'}, {'cat': 'math.SG', 'label': 'Symplectic Geometry'}, {'cat': 'cs.AI', 'label': 'Artificial Intelligence'}, {'cat': 'cs.CL', 'label': 'Computation and Language'}, {'cat': 'cs.CC', 'label': 'Computational Complexity'}, {'cat': 'cs.CE', 'label': 'Computational Engineering, Finance, and Science'}, {'cat': 'cs.CG', 'label': 'Computational Geometry'}, {'cat': 'cs.GT', 'label': 'Computer Science and Game Theory'}, {'cat': 'cs.CV', 'label': 'Computer Vision and Pattern Recognition'}, {'cat': 'cs.CY', 'label': 'Computers and Society'}, {'cat': 'cs.CR', 'label': 'Cryptography and Security'}, {'cat': 'cs.DS', 'label': 'Data Structures and Algorithms'}, {'cat': 'cs.DB', 'label': 'Databases'}, {'cat': 'cs.DL', 'label': 'Digital Libraries'}, {'cat': 'cs.DM', 'label': 'Discrete Mathematics'}, {'cat': 'cs.DC', 'label': 'Distributed, Parallel, and Cluster Computing'}, {'cat': 'cs.ET', 'label': 'Emerging Technologies'}, {'cat': 'cs.FL', 'label': 'Formal Languages and Automata Theory'}, {'cat': 'cs.GL', 'label': 'General Literature'}, {'cat': 'cs.GR', 'label': 'Graphics'}, {'cat': 'cs.AR', 'label': 'Hardware Architecture'}, {'cat': 'cs.HC', 'label': 'Human-Computer Interaction'}, {'cat': 'cs.IR', 'label': 'Information Retrieval'}, {'cat': 'cs.IT', 'label': 'Information Theory'}, {'cat': 'cs.LG', 'label': 'Learning'}, {'cat': 'cs.LO', 'label': 'Logic in Computer Science'}, {'cat': 'cs.MS', 'label': 'Mathematical Software'}, {'cat': 'cs.MA', 'label': 'Multiagent Systems'}, {'cat': 'cs.MM', 'label': 'Multimedia'}, {'cat': 'cs.NI', 'label': 'Networking and Internet Architecture'}, {'cat': 'cs.NE', 'label': 'Neural and Evolutionary Computing'}, {'cat': 'cs.NA', 'label': 'Numerical Analysis'}, {'cat': 'cs.OS', 'label': 'Operating Systems'}, {'cat': 'cs.OH', 'label': 'Other Computer Science'}, {'cat': 'cs.PF', 'label': 'Performance'}, {'cat': 'cs.PL', 'label': 'Programming Languages'}, {'cat': 'cs.RO', 'label': 'Robotics'}, {'cat': 'cs.SI', 'label': 'Social and Information Networks'}, {'cat': 'cs.SE', 'label': 'Software Engineering'}, {'cat': 'cs.SD', 'label': 'Sound'}, {'cat': 'cs.SC', 'label': 'Symbolic Computation'}, {'cat': 'cs.SY', 'label': 'Systems and Control'}, {'cat': 'q-bio.BM', 'label': 'Biomolecules'}, {'cat': 'q-bio.GN', 'label': 'Genomics'}, {'cat': 'q-bio.MN', 'label': 'Molecular Networks'}, {'cat': 'q-bio.SC', 'label': 'Subcellular Processes'}, {'cat': 'q-bio.CB', 'label': 'Cell Behavior'}, {'cat': 'q-bio.NC', 'label': 'Neurons and Cognition'}, {'cat': 'q-bio.TO', 'label': 'Tissues and Organs'}, {'cat': 'q-bio.PE', 'label': 'Populations and Evolution'}, {'cat': 'q-bio.QM', 'label': 'Quantitative Methods'}, {'cat': 'q-bio.OT', 'label': 'Other'}, {'cat': 'q-fin.PR', 'label': 'Pricing of Securities'}, {'cat': 'q-fin.RM', 'label': 'Risk Management'}, {'cat': 'q-fin.PM', 'label': 'Portfolio Management'}, {'cat': 'q-fin.TR', 'label': 'Trading and Microstructure'}, {'cat': 'q-fin.MF', 'label': 'Mathematical Finance'}, {'cat': 'q-fin.CP', 'label': 'Computational Finance'}, {'cat': 'q-fin.ST', 'label': 'Statistical Finance'}, {'cat': 'q-fin.GN', 'label': 'General Finance'}, {'cat': 'q-fin.EC', 'label': 'Economics'}, {'cat': 'stat.AP', 'label': 'Applications'}, {'cat': 'stat.CO', 'label': 'Computation'}, {'cat': 'stat.ML', 'label': 'Machine Learning'}, {'cat': 'stat.ME', 'label': 'Methodology'}, {'cat': 'stat.OT', 'label': 'Other Statistics'}, {'cat': 'stat.TH', 'label': 'Theory'}
      ],
      render: {
        item: function(item, escape) {
            return '<div>' +
                (item.cat ? '<span class="cat">' + escape(item.cat) + ' - </span>' : '') +
                (item.label ? '<span class="label">' + escape(item.label) + '</span>' : '') +
            '</div>';
        },
        option: function(item, escape) {
            var label = item.cat || item.label;
            var caption = item.cat ? item.label : null;
            return '<div>' +
                '<span class="label">' + escape(label) + ' - </span>' +
                (caption ? '<span class="caption">' + escape(caption) + '</span>' : '') +
            '</div>';
        }
      },
      create: function(input) {
          return {
              cat: input,
              label: input
          }
      }
  });
  var categorySelect = $select[0].selectize;

  var $select = $('#creator').selectize({
      delimiter: ',',
      persist: false,
      maxItems: 1,
      plugins: ['remove_button', 'enter_key_submit'],
      onInitialize: function () {
        this.on('submit', function () {
          this.$input.closest('form').submit();
        }, this);
      },
      valueField: 'cat',
      labelField: 'label',
      searchField: ['cat', 'label'],
      options: [
        {'cat': 'TeX', 'label': '14174'}, {'cat': 'SM', 'label': '13097'}, {'cat': 'OriginLab', 'label': '8876'}, {'cat': 'GIMP', 'label': '10730'}, {'cat': 'R', 'label': '9195'}, {'cat': 'MATLAB', 'label': '50808'}, {'cat': 'Mathematica', 'label': '27606'}, {'cat': 'ImageMagick', 'label': '6323'}, {'cat': 'jpeg2ps', 'label': '4198'}, {'cat': 'fig2dev', 'label': '16680'}, {'cat': 'PGPLOT', 'label': '6259'}, {'cat': 'cairo', 'label': '22867'}, {'cat': 'gnuplot', 'label': '20207'}, {'cat': 'Grace', 'label': '11678'}, {'cat': 'PScript5', 'label': '3704'}, {'cat': 'matplotlib', 'label': '47145'}, {'cat': '', 'label': '2578'}, {'cat': 'Keynote', 'label': '2735'}, {'cat': 'LaTeX', 'label': '2321'}, {'cat': 'Illustrator', 'label': '14408'}, {'cat': 'inkscape', 'label': '2388'}, {'cat': 'PowerPoint', 'label': '3487'}, {'cat': 'dvips', 'label': '11680'}, {'cat': 'Preview', 'label': '1530'}, {'cat': 'FreeHEP', 'label': '1283'}, {'cat': 'HIGZ', 'label': '7000'}, {'cat': 'CorelDRAW', 'label': '4745'}, {'cat': 'PSCRIPT', 'label': '1659'}, {'cat': 'gnome-screenshot', 'label': '1058'}, {'cat': 'Wolfram', 'label': '1180'}, {'cat': 'xmgr', 'label': '1859'}, {'cat': 'TECPLOT', 'label': '907'}, {'cat': 'Acrobat', 'label': '3996'}, {'cat': 'Unknown', 'label': '1086'}, {'cat': 'Draw', 'label': '855'}, {'cat': 'Unified', 'label': '960'}, {'cat': 'XV', 'label': '2243'}, {'cat': 'IDL', 'label': '19590'}, {'cat': 'fko', 'label': '811'}, {'cat': 'ImageReady', 'label': '755'}, {'cat': 'Sun', 'label': '761'}, {'cat': 'Maple', 'label': '760'}, {'cat': 'Office', 'label': '704'}, {'cat': 'Ipe', 'label': '2662'}, {'cat': 'pdfresizer', 'label': '628'}, {'cat': 'Chromium', 'label': '597'}, {'cat': 'Tk', 'label': '595'}, {'cat': 'Ghostscript', 'label': '10191'}, {'cat': 'dvipsk', 'label': '835'}, {'cat': 'pnmtops', 'label': '532'}, {'cat': 'Mathematica-PSRender', 'label': '511'}, {'cat': 'ROOT', 'label': '14147'}, {'cat': 'IgorPro', 'label': '501'}, {'cat': 'EPS-conv', 'label': '530'}, {'cat': 'TRIUMF', 'label': '419'}, {'cat': 'AIPS', 'label': '364'}, {'cat': 'GTVIRT', 'label': '1026'}, {'cat': 'Administrator', 'label': '378'}, {'cat': '3-Heights', 'label': '430'}, {'cat': 'Visio', 'label': '829'}, {'cat': 'ImageMark', 'label': '317'}, {'cat': 'Quartz', 'label': '315'}, {'cat': 'Impress', 'label': '308'}, {'cat': 'Igor', 'label': '467'}, {'cat': '0', 'label': '359'}, {'cat': 'Photoshop', 'label': '4403'}, {'cat': 'OmniGraffle', 'label': '1933'}, {'cat': 'ACE/gr', 'label': '750'}, {'cat': 'Photo', 'label': '227'}, {'cat': 'imgtops', 'label': '233'}, {'cat': '()', 'label': '214'}, {'cat': 'MapleV', 'label': '202'}, {'cat': 'NT', 'label': '207'}, {'cat': 'jpeg2eps', 'label': '194'}, {'cat': 'Gist', 'label': '185'}, {'cat': 'QtiPlot', 'label': '174'}, {'cat': 'GLE', 'label': '344'}, {'cat': 'user', 'label': '319'}, {'cat': 'xpdf/pdftops', 'label': '317'}, {'cat': 'GraphicConverter', 'label': '1195'}, {'cat': 'Pages', 'label': '154'}, {'cat': 'Ipelib', 'label': '660'}, {'cat': 'Online2PDF', 'label': '147'}, {'cat': 'Serif', 'label': '204'}, {'cat': 'Shotwell', 'label': '447'}, {'cat': 'Jasc', 'label': '181'}, {'cat': 'EpsGraphics', 'label': '133'}, {'cat': 'Google', 'label': '139'}, {'cat': 'Tgif', 'label': '726'}, {'cat': 'Shutter', 'label': '123'}, {'cat': 'TriMetrix', 'label': '120'}, {'cat': 'sgi2ueps', 'label': '118'}, {'cat': 'Feynman', 'label': '115'}, {'cat': 'PSIKern', 'label': '111'}, {'cat': 'Aladdin', 'label': '191'}, {'cat': 'PyX', 'label': '359'}, {'cat': 'Lick', 'label': '209'}, {'cat': 'LibreOffice', 'label': '447'}, {'cat': 'module', 'label': '160'}, {'cat': 'KaleidaGraph', 'label': '623'}, {'cat': 'Word', 'label': '334'}, {'cat': 'David', 'label': '174'}, {'cat': 'Mayura', 'label': '371'}, {'cat': 'proFit', 'label': '90'}, {'cat': 'Dia', 'label': '275'}, {'cat': 'Zamzar', 'label': '81'}, {'cat': 'GKS', 'label': '76'}, {'cat': 'GRA2PS', 'label': '307'}, {'cat': 'yExport', 'label': '124'}, {'cat': 'Image', 'label': '204'}, {'cat': 'https', 'label': '70'}, {'cat': 'XnView', 'label': '72'}, {'cat': 'Micrografx', 'label': '79'}, {'cat': 'pdftk', 'label': '174'}, {'cat': 'psmerge', 'label': '66'}, {'cat': 'Canvas', 'label': '423'}, {'cat': 'GL2PS', 'label': '136'}, {'cat': 'Autodesk', 'label': '62'}, {'cat': 'Paint', 'label': '377'}, {'cat': 'VTK', 'label': '62'}, {'cat': 'BI', 'label': '62'}, {'cat': 'RAD', 'label': '61'}, {'cat': 'Apache', 'label': '82'}, {'cat': 'Picasa', 'label': '63'}, {'cat': 'meitu', 'label': '58'}, {'cat': 'TpX', 'label': '57'}, {'cat': 'AutoCAD', 'label': '108'}, {'cat': 'PrimoPDF', 'label': '57'}, {'cat': 'Anteprima', 'label': '55'}, {'cat': 'GPLOT', 'label': '53'}, {'cat': 'GSS', 'label': '53'}, {'cat': 'Graphic', 'label': '74'}, {'cat': 'Excel', 'label': '210'}, {'cat': 'admin', 'label': '115'}, {'cat': 'InDesign', 'label': '87'}, {'cat': 'SciPlot', 'label': '61'}, {'cat': 'SigmaPlot', 'label': '114'}, {'cat': 'tiff2ps', 'label': '53'}, {'cat': 'プレビュー', 'label': '52'}, {'cat': 'GeoGebra', 'label': '51'}, {'cat': 'Octave', 'label': '50'}, {'cat': 'Tailor', 'label': '50'}, {'cat': '用户', 'label': '54'}, {'cat': 'DeskScan', 'label': '53'}, {'cat': 'MetaPost', 'label': '314'}, {'cat': 'SM230', 'label': '48'}, {'cat': 'C-PLOT', 'label': '51'}, {'cat': 'LaTeXiT', 'label': '47'}, {'cat': 'imgtops2', 'label': '47'}, {'cat': 'iDraw', 'label': '77'}, {'cat': 'dasmus', 'label': '49'}, {'cat': 'FreeHand', 'label': '229'}, {'cat': 'gelis', 'label': '44'}, {'cat': 'Id', 'label': '55'}, {'cat': 'Aperçu', 'label': '43'}, {'cat': '050ImageMagick', 'label': '48'}, {'cat': 'Diagramm', 'label': '44'}, {'cat': 'libplot', 'label': '114'}, {'cat': 'Axum', 'label': '77'}, {'cat': 'Dietrich', 'label': '43'}, {'cat': 'Mongo2k', 'label': '41'}, {'cat': '预览', 'label': '41'}, {'cat': 'ESO-MIDAS', 'label': '40'}, {'cat': 'PDFium', 'label': '40'}, {'cat': 'a10004', 'label': '40'}, {'cat': 'ctioga2', 'label': '54'}, {'cat': 'IrfanView', 'label': '38'}, {'cat': 'Xara', 'label': '44'}, {'cat': 'Xvgr', 'label': '52'}, {'cat': 'ACDSee', 'label': '53'}, {'cat': 'PS4', 'label': '182'}, {'cat': 'EpsGraphics2D', 'label': '70'}, {'cat': 'Frank', 'label': '67'}, {'cat': 'KnotPlot', 'label': '37'}, {'cat': 'R/RGL', 'label': '37'}, {'cat': 'UnknownApplication', 'label': '37'}, {'cat': 'Veusz', 'label': '492'}, {'cat': 'diagrams', 'label': '37'}, {'cat': 'GraphicsMagick', 'label': '55'}, {'cat': 'CLARIS', 'label': '37'}, {'cat': '050MATLAB', 'label': '208'}, {'cat': 'lenovo', 'label': '73'}, {'cat': 'programmed', 'label': '36'}, {'cat': 'Artifex', 'label': '36'}, {'cat': 'MiKTeX', 'label': '184'}, {'cat': 'wPDF', 'label': '35'}, {'cat': 'SuperPaint', 'label': '36'}, {'cat': 'WJpeg2ps', 'label': '34'}, {'cat': 'Diagram', 'label': '34'}, {'cat': 'Greenshot', 'label': '33'}, {'cat': 'PIL', 'label': '33'}, {'cat': 'Vista', 'label': '33'}, {'cat': 'GMT', 'label': '32'}, {'cat': 'RAL', 'label': '204'}, {'cat': 'Visualization', 'label': '33'}, {'cat': 'Writer', 'label': '32'}, {'cat': 'Alex', 'label': '85'}, {'cat': '/fig2dev', 'label': '32'}, {'cat': 'Corel', 'label': '233'}, {'cat': 'PDFaid', 'label': '31'}, {'cat': 'akartavt', 'label': '31'}, {'cat': 'dell', 'label': '50'}, {'cat': 'figps', 'label': '31'}, {'cat': '/cygdrive/c/windows/fig2dev', 'label': '31'}, {'cat': 'Altsys', 'label': '30'}, {'cat': 'Jmol', 'label': '31'}, {'cat': 'Word2TeX', 'label': '32'}, {'cat': 'CLShan', 'label': '28'}, {'cat': 'ImageEn', 'label': '28'}, {'cat': 'Tailor_Mac_To_EPS', 'label': '28'}, {'cat': 'graphviz', 'label': '154'}, {'cat': 'thomasfiedler', 'label': '28'}, {'cat': 'Asymptote', 'label': '187'}, {'cat': 'psk', 'label': '27'}, {'cat': 'ACD', 'label': '29'}, {'cat': 'Aspose', 'label': '26'}, {'cat': 'elendil', 'label': '26'}, {'cat': 'jlibeps', 'label': '28'}, {'cat': 'stefano', 'label': '36'}, {'cat': 'Pyxplot', 'label': '73'}, {'cat': 'marco', 'label': '52'}, {'cat': 'CoHort', 'label': '35'}, {'cat': 'Markus', 'label': '39'}, {'cat': 'PageDraw', 'label': '25'}, {'cat': 'hp2xx', 'label': '31'}, {'cat': 'Maurice', 'label': '26'}, {'cat': 'PS5', 'label': '72'}, {'cat': 'Camelot', 'label': '22'}, {'cat': 'DECW', 'label': '23'}, {'cat': 'FeynArts', 'label': '22'}, {'cat': 'Mirage', 'label': '22'}, {'cat': 'PDF24', 'label': '22'}, {'cat': 'Pajek', 'label': '25'}, {'cat': 'convert-jpg-to-pdf', 'label': '22'}, {'cat': '3-D', 'label': '21'}, {'cat': 'Create', 'label': '21'}, {'cat': 'Macromedia', 'label': '36'}, {'cat': 'Windows', 'label': '44'}, {'cat': 'bcarry', 'label': '22'}, {'cat': 'garel', 'label': '29'}, {'cat': 'Andrea', 'label': '52'}, {'cat': 'FeynDiagram', 'label': '66'}, {'cat': 'S-PLUS', 'label': '42'}, {'cat': 'Topdraw', 'label': '29'}, {'cat': 'Vorschau', 'label': '21'}, {'cat': 'WPS', 'label': '35'}, {'cat': 'boram', 'label': '20'}, {'cat': 'chavanis', 'label': '29'}, {'cat': 'dvi2ps', 'label': '20'}, {'cat': 'grass', 'label': '20'}
      ],
      render: {
        item: function(item, escape) {
            return '<div>' +
                (item.cat ? '<span class="cat">' + escape(item.cat) + ' - </span>' : '') +
                (item.label ? '<span class="label">' + escape(item.label) + '</span>' : '') +
            '</div>';
        },
        option: function(item, escape) {
            var label = item.cat || item.label;
            var caption = item.cat ? item.label : null;
            return '<div>' +
                '<span class="label">' + escape(label) + ' - </span>' +
                (caption ? '<span class="caption">' + escape(caption) + '</span>' : '') +
            '</div>';
        }
      },
      create: function(input) {
          return {
              cat: input,
              label: input
          }
      }
  });
  var creatorSelect = $select[0].selectize;

  var $ifSelect = $('#imageformat').selectize({
      create: false,
      // sortField: 'text'
      plugins: ['remove_button', 'enter_key_submit'],
      onInitialize: function () {
        this.on('submit', function () {
          this.$input.closest('form').submit();
        }, this);
      },
  });
  var ifSelect = $ifSelect[0].selectize;

  var titleSelect = $('#title').selectize({
      create: true,
      // sortField: 'text'
      maxItems: 1,
      plugins: ['remove_button', 'enter_key_submit'],
      onInitialize: function () {
        this.on('submit', function () {
          this.$input.closest('form').submit();
        }, this);
      },
      persist: true,
  });
  var titleSelect = titleSelect[0].selectize;

  var captionSelect = $('#caption').selectize({
      create: true,
      // sortField: 'text'
      maxItems: 1,
      plugins: ['remove_button', 'enter_key_submit'],
      onInitialize: function () {
        this.on('submit', function () {
          this.$input.closest('form').submit();
        }, this);
      },
  });
  var captionSelect = captionSelect[0].selectize;

  // activate tooltips
  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

  // $('.input-daterange input').each(function() {
  //   $(this).datepicker('clearDates');
  // });

  $('[data-toggle="popover"]').popover({
    offset: '50',
    // placement: 'top',
    // trigger: 'click',
  });
  // $('.popover-dismiss').popover({
  //   trigger: 'focus'
  // })

  {% if prev_image_id %}
    $("#image_id").val( {{ prev_image_id }} );
  {% endif %}

  {% if embedding %}
    console.log({{embedding|tojson}});
    var emVal = {{embedding|tojson}};
    $("#embedding").val(emVal);
  {% endif %}

  console.log({{search_select|tojson}});
  var emVal = {{search_select|tojson}};
  if(emVal === "on") {
    console.log("toggling checkbox");
    $("#search_select").val("on");
    checkbox.checked = 1;
  }
  toggleMode();


  {% if category or imageformat or author or prediction or title or creator or caption or date_start or date_end %}
    console.log("some filters active");
    // var collapsible = document.getElementsByClassName("collapsible");
    // collapsible.collapse("toggle");
    $("#filter-content").collapse('toggle');
  {% endif %}

  {% if category %}
    console.log({{category|tojson}});
    var catVal = {{category|tojson}};
    categorySelect.setValue(catVal.split(","), 1);
  {% endif %}
  // selectize.setValue(["cs.CV","astro-ph.GA"], 1);

  {% if imageformat %}
    console.log({{imageformat|tojson}});
    var imVal = {{imageformat|tojson}};
    ifSelect.setValue(imVal, 1);
  {% endif %}
  // selectize.setValue(["cs.CV","astro-ph.GA"], 1);

  {% if author %}
    console.log({{author|tojson}});
    var authorVal = {{author|tojson}};
    // $("#author").val(authorVal);
    authorSelect.setValue(authorVal, 1);
  {% endif %}

  {% if prediction %}
    console.log({{prediction|tojson}});
    var predVal = {{prediction|tojson}};
    // $("#prediction").val(predVal);
    predictionSelect.addOption({value:predVal,text:predVal});
    predictionSelect.setValue(predVal, 1);
  {% endif %}

  {% if title %}
    console.log({{title|tojson}});
    var titleVal = {{title|tojson}};
    // $("#prediction").val(predVal);
    titleSelect.addOption({value:titleVal,text:titleVal});
    titleSelect.setValue(titleVal, 1);
  {% endif %}

  {% if creator %}
    console.log({{creator|tojson}});
    var creatorVal = {{creator|tojson}};
    // $("#prediction").val(predVal);
    creatorSelect.setValue(creatorVal, 1);
  {% endif %}

  {% if caption %}
    console.log({{caption|tojson}});
    var captionVal = {{caption|tojson}};
    // $("#prediction").val(predVal);
    captionSelect.addOption({value:captionVal,text:captionVal});
    captionSelect.setValue(captionVal, 1);
  {% endif %}

  {% if date_start %}
    console.log({{date_start|tojson}});
    var dsVal = {{date_start|tojson}};
    var ds = document.getElementById("date-start");
    ds.value = dsVal;
  {% endif %}

  {% if date_end %}
    console.log({{date_end|tojson}});
    var deVal = {{date_end|tojson}};
    var de = document.getElementById("date-end");
    de.value = deVal;
  {% endif %}

  // window.MathJax = {
  //   tex: {
  //     inlineMath: [['$', '$'], ['\\(', '\\)']]
  //   }
  // };

  $('#container').imagesLoaded()
  .always( function( instance ) {
    console.log('all images loaded');
  })
  .done( function( instance ) {
    console.log('all images successfully loaded');
  })
  .fail( function() {
    console.log('all images loaded, at least one is broken');
  })
  .progress( function( instance, image ) {
    var result = image.isLoaded ? 'loaded' : 'broken';
    console.log( 'image is ' + result + ' for ' + image.img.src );
  });
});

</script>