def get_css_boostrap():
    return """/*!
 * Bootstrap v3.3.1 (http://getbootstrap.com)
 * Copyright 2011-2015 Twitter, Inc.
 * Licensed under MIT (https://github.com/twbs/bootstrap/blob/master/LICENSE)
 */

/*! normalize.css v3.0.2 | MIT License | git.io/normalize */
html {
    font-family: sans-serif;
    -webkit-text-size-adjust: 100%;
        -ms-text-size-adjust: 100%;
  }
  body {
    margin: 0;
  }
  article,
  aside,
  figcaption,
  figure,
  footer,
  header,
  hgroup,
  main,
  menu,
  nav,
  section {
    display: block;
  }
  audio,
  canvas,
  progress,
  video {
    display: inline-block;
    vertical-align: baseline;
  }
  audio:not([controls]) {
    display: none;
    height: 0;
  }
  [hidden],
  template {
    display: none;
  }
  a {
    background-color: transparent;
  }
  a:active,
  a:hover {
    outline: 0;
  }
  abbr[title] {
    border-bottom: 1px dotted;
  }
  b,
  strong {
    font-weight: bold;
  }
  dfn {
    font-style: italic;
  }
  h1 {
    margin: .67em 0;
    font-size: 2em;
  }
  mark {
    color: #000;
    background: #ff0;
  }
  small {
    font-size: 80%;
  }
  sub,
  sup {
    position: relative;
    font-size: 75%;
    line-height: 0;
    vertical-align: baseline;
  }
  sup {
    top: -.5em;
  }
  sub {
    bottom: -.25em;
  }
  img {
    border: 0;
  }
  svg:not(:root) {
    overflow: hidden;
  }
  figure {
    margin: 1em 40px;
  }
  hr {
    height: 0;
    -webkit-box-sizing: content-box;
       -moz-box-sizing: content-box;
            box-sizing: content-box;
  }
  pre {
    overflow: auto;
  }
  code,
  kbd,
  pre,
  samp {
    font-family: monospace, monospace;
    font-size: 1em;
  }
  button,
  input,
  optgroup,
  select,
  textarea {
    margin: 0;
    font: inherit;
    color: inherit;
  }
  button {
    overflow: visible;
  }
  button,
  select {
    text-transform: none;
  }
  button,
  html input[type='button'],
  input[type='reset'],
  input[type='submit'] {
    -webkit-appearance: button;
    cursor: pointer;
  }
  button[disabled],
  html input[disabled] {
    cursor: default;
  }
  button::-moz-focus-inner,
  input::-moz-focus-inner {
    padding: 0;
    border: 0;
  }
  input {
    line-height: normal;
  }
  input[type='checkbox'],
  input[type='radio'] {
    -webkit-box-sizing: border-box;
       -moz-box-sizing: border-box;
            box-sizing: border-box;
    padding: 0;
  }
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    height: auto;
  }
  input[type='search'] {
    -webkit-box-sizing: content-box;
       -moz-box-sizing: content-box;
            box-sizing: content-box;
    -webkit-appearance: textfield;
  }
  input[type='search']::-webkit-search-cancel-button,
  input[type='search']::-webkit-search-decoration {
    -webkit-appearance: none;
  }
  fieldset {
    padding: .35em .625em .75em;
    margin: 0 2px;
    border: 1px solid #c0c0c0;
  }
  legend {
    padding: 0;
    border: 0;
  }
  textarea {
    overflow: auto;
  }
  optgroup {
    font-weight: bold;
  }
  table {
    border-spacing: 0;
    border-collapse: collapse;
  }
  td,
  th {
    padding: 0;
  }
  /*! Source: https://github.com/h5bp/html5-boilerplate/blob/master/src/css/main.css */
  @media print {
    *,
    *:before,
    *:after {
      color: #000;
      background: transparent;
      text-shadow: none !important;
      -webkit-box-shadow: none !important;
              box-shadow: none !important;
    }
    a,
    a:visited {
      text-decoration: underline;
    }
    abbr[title]:after {
      content: ' (' attr(title) ')';
    }
    a[href^='#']:after,
    a[href^='javascript:']:after {
      content: '';
    }
    pre,
    blockquote {
      border: 1px solid #999;
  
      page-break-inside: avoid;
    }
    thead {
      display: table-header-group;
    }
    tr,
    img {
      page-break-inside: avoid;
    }
    img {
      max-width: 100% !important;
    }
    p,
    h2,
    h3 {
      orphans: 3;
      widows: 3;
    }
    h2,
    h3 {
      page-break-after: avoid;
    }
    select {
      background: #fff !important;
    }
    .navbar {
      display: none;
    }
    .btn > .caret,
    .dropup > .btn > .caret {
      border-top-color: #000 !important;
    }
    .label {
      border: 1px solid #000;
    }
    .table {
      border-collapse: collapse !important;
    }
    .table td,
    .table th {
      background-color: #fff;
    }
    .table-bordered th,
    .table-bordered td {
      border: 1px solid #ddd;
    }
  }
  * {
    -webkit-box-sizing: border-box;
       -moz-box-sizing: border-box;
            box-sizing: border-box;
  }
  *:before,
  *:after {
    -webkit-box-sizing: border-box;
       -moz-box-sizing: border-box;
            box-sizing: border-box;
  }
  html {
    font-size: 10px;
  
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
  }
  body {
    font-family: 'Helvetica Neue', Helvetica, Arial, 'Open Sans', sans-serif;
    font-size: 14px;
    line-height: 1.42857143;
    color: #36414c;
    background-color: #fff;
  }
  input,
  button,
  select,
  textarea {
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
  }
  a {
    color: #36414c;
    text-decoration: none;
  }
  a:hover,
  a:focus {
    color: #161b1f;
    text-decoration: underline;
  }
  a:focus {
    outline: thin dotted;
    outline: 5px auto -webkit-focus-ring-color;
    outline-offset: -2px;
  }
  figure {
    margin: 0;
  }
  img {
    vertical-align: middle;
  }
  .img-responsive,
  .thumbnail > img,
  .thumbnail a > img,
  .carousel-inner > .item > img,
  .carousel-inner > .item > a > img {
    display: block;
    max-width: 100%;
    height: auto;
  }
  .img-rounded {
    border-radius: 6px;
  }
  .img-thumbnail {
    display: inline-block;
    max-width: 100%;
    height: auto;
    padding: 4px;
    line-height: 1.42857143;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    -webkit-transition: all .2s ease-in-out;
         -o-transition: all .2s ease-in-out;
            transition: all .2s ease-in-out;
  }
  .img-circle {
    border-radius: 50%;
  }
  hr {
    margin-top: 20px;
    margin-bottom: 20px;
    border: 0;
    border-top: 1px solid #d1d8dd;
  }
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
  }
  .sr-only-focusable:active,
  .sr-only-focusable:focus {
    position: static;
    width: auto;
    height: auto;
    margin: 0;
    overflow: visible;
    clip: auto;
  }
  h1,
  h2,
  h3,
  h4,
  h5,
  h6,
  .h1,
  .h2,
  .h3,
  .h4,
  .h5,
  .h6 {
    font-family: inherit;
    font-weight: 500;
    line-height: 1.3em;
    color: inherit;
  }
  h1 small,
  h2 small,
  h3 small,
  h4 small,
  h5 small,
  h6 small,
  .h1 small,
  .h2 small,
  .h3 small,
  .h4 small,
  .h5 small,
  .h6 small,
  h1 .small,
  h2 .small,
  h3 .small,
  h4 .small,
  h5 .small,
  h6 .small,
  .h1 .small,
  .h2 .small,
  .h3 .small,
  .h4 .small,
  .h5 .small,
  .h6 .small {
    font-weight: normal;
    line-height: 1;
    color: #777;
  }
  h1,
  .h1,
  h2,
  .h2,
  h3,
  .h3 {
    margin-top: 20px;
    margin-bottom: 10px;
  }
  h1 small,
  .h1 small,
  h2 small,
  .h2 small,
  h3 small,
  .h3 small,
  h1 .small,
  .h1 .small,
  h2 .small,
  .h2 .small,
  h3 .small,
  .h3 .small {
    font-size: 65%;
  }
  h4,
  .h4,
  h5,
  .h5,
  h6,
  .h6 {
    margin-top: 10px;
    margin-bottom: 10px;
  }
  h4 small,
  .h4 small,
  h5 small,
  .h5 small,
  h6 small,
  .h6 small,
  h4 .small,
  .h4 .small,
  h5 .small,
  .h5 .small,
  h6 .small,
  .h6 .small {
    font-size: 75%;
  }
  h1,
  .h1 {
    font-size: 24px;
  }
  h2,
  .h2 {
    font-size: 20px;
  }
  h3,
  .h3 {
    font-size: 18px;
  }
  h4,
  .h4 {
    font-size: 16px;
  }
  h5,
  .h5 {
    font-size: 14px;
  }
  h6,
  .h6 {
    font-size: 12px;
  }
  p {
    margin: 0 0 10px;
  }
  .lead {
    margin-bottom: 20px;
    font-size: 16px;
    font-weight: 300;
    line-height: 1.4;
  }
  @media (min-width: 768px) {
    .lead {
      font-size: 21px;
    }
  }
  small,
  .small {
    font-size: 85%;
  }
  mark,
  .mark {
    padding: .2em;
    background-color: transparent;
  }
  .text-left {
    text-align: left;
  }
  .text-right {
    text-align: right;
  }
  .text-center {
    text-align: center;
  }
  .text-justify {
    text-align: justify;
  }
  .text-nowrap {
    white-space: nowrap;
  }
  .text-lowercase {
    text-transform: lowercase;
  }
  .text-uppercase {
    text-transform: uppercase;
  }
  .text-capitalize {
    text-transform: capitalize;
  }
  .text-muted {
    color: #8d99a6;
  }
  .text-primary {
    color: #5e64ff;
  }
  a.text-primary:hover {
    color: #2b33ff;
  }
  .text-success {
    color: #98d85b;
  }
  a.text-success:hover {
    color: #7ece32;
  }
  .text-info {
    color: #935eff;
  }
  a.text-info:hover {
    color: #712bff;
  }
  .text-warning {
    color: #ffa00a;
  }
  a.text-warning:hover {
    color: #d68300;
  }
  .text-danger {
    color: #ff5858;
  }
  a.text-danger:hover {
    color: #ff2525;
  }
  .bg-primary {
    color: #fff;
    background-color: #5e64ff;
  }
  a.bg-primary:hover {
    background-color: #2b33ff;
  }
  .bg-success {
    background-color: transparent;
  }
  a.bg-success:hover {
    background-color: rgba(0, 0, 0, 0);
  }
  .bg-info {
    background-color: transparent;
  }
  a.bg-info:hover {
    background-color: rgba(0, 0, 0, 0);
  }
  .bg-warning {
    background-color: transparent;
  }
  a.bg-warning:hover {
    background-color: rgba(0, 0, 0, 0);
  }
  .bg-danger {
    background-color: transparent;
  }
  a.bg-danger:hover {
    background-color: rgba(0, 0, 0, 0);
  }
  .page-header {
    padding-bottom: 9px;
    margin: 40px 0 20px;
    border-bottom: 1px solid #eee;
  }
  ul,
  ol {
    margin-top: 0;
    margin-bottom: 10px;
  }
  ul ul,
  ol ul,
  ul ol,
  ol ol {
    margin-bottom: 0;
  }
  .list-unstyled {
    padding-left: 0;
    list-style: none;
  }
  .list-inline {
    padding-left: 0;
    margin-left: -5px;
    list-style: none;
  }
  .list-inline > li {
    display: inline-block;
    padding-right: 5px;
    padding-left: 5px;
  }
  dl {
    margin-top: 0;
    margin-bottom: 20px;
  }
  dt,
  dd {
    line-height: 1.42857143;
  }
  dt {
    font-weight: bold;
  }
  dd {
    margin-left: 0;
  }
  @media (min-width: 768px) {
    .dl-horizontal dt {
      float: left;
      width: 160px;
      overflow: hidden;
      clear: left;
      text-align: right;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .dl-horizontal dd {
      margin-left: 180px;
    }
  }
  abbr[title],
  abbr[data-original-title] {
    cursor: help;
    border-bottom: 1px dotted #777;
  }
  .initialism {
    font-size: 90%;
    text-transform: uppercase;
  }
  blockquote {
    padding: 10px 20px;
    margin: 0 0 20px;
    font-size: 17.5px;
    border-left: 5px solid #eee;
  }
  blockquote p:last-child,
  blockquote ul:last-child,
  blockquote ol:last-child {
    margin-bottom: 0;
  }
  blockquote footer,
  blockquote small,
  blockquote .small {
    display: block;
    font-size: 80%;
    line-height: 1.42857143;
    color: #777;
  }
  blockquote footer:before,
  blockquote small:before,
  blockquote .small:before {
    content: 'NONE';
  }
  .blockquote-reverse,
  blockquote.pull-right {
    padding-right: 15px;
    padding-left: 0;
    text-align: right;
    border-right: 5px solid #eee;
    border-left: 0;
  }
  .blockquote-reverse footer:before,
  blockquote.pull-right footer:before,
  .blockquote-reverse small:before,
  blockquote.pull-right small:before,
  .blockquote-reverse .small:before,
  blockquote.pull-right .small:before {
    content: '';
  }
  .blockquote-reverse footer:after,
  blockquote.pull-right footer:after,
  .blockquote-reverse small:after,
  blockquote.pull-right small:after,
  .blockquote-reverse .small:after,
  blockquote.pull-right .small:after {
    content: 'NONE';
  }
  address {
    margin-bottom: 20px;
    font-style: normal;
    line-height: 1.42857143;
  }
  code,
  kbd,
  pre,
  samp {
    font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
  }
  code {
    padding: 2px 4px;
    font-size: 90%;
    color: #c7254e;
    background-color: #f9f2f4;
    border-radius: 4px;
  }
  kbd {
    padding: 2px 4px;
    font-size: 90%;
    color: #fff;
    background-color: #333;
    border-radius: 3px;
    -webkit-box-shadow: inset 0 -1px 0 rgba(0, 0, 0, .25);
            box-shadow: inset 0 -1px 0 rgba(0, 0, 0, .25);
  }
  kbd kbd {
    padding: 0;
    font-size: 100%;
    font-weight: bold;
    -webkit-box-shadow: none;
            box-shadow: none;
  }
  pre {
    display: block;
    padding: 9.5px;
    margin: 0 0 10px;
    font-size: 13px;
    line-height: 1.42857143;
    color: #333;
    word-break: break-all;
    word-wrap: break-word;
    background-color: #f5f5f5;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  pre code {
    padding: 0;
    font-size: inherit;
    color: inherit;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 0;
  }
  .pre-scrollable {
    max-height: 340px;
    overflow-y: scroll;
  }
  .container {
    padding-right: 15px;
    padding-left: 15px;
    margin-right: auto;
    margin-left: auto;
  }
  @media (min-width: 768px) {
    .container {
      width: 750px;
    }
  }
  @media (min-width: 992px) {
    .container {
      width: 970px;
    }
  }
  @media (min-width: 1200px) {
    .container {
      width: 1170px;
    }
  }
  .container-fluid {
    padding-right: 15px;
    padding-left: 15px;
    margin-right: auto;
    margin-left: auto;
  }
  .row {
    margin-right: -15px;
    margin-left: -15px;
  }
  .col-xs-1, .col-sm-1, .col-md-1, .col-lg-1, .col-xs-2, .col-sm-2, .col-md-2, .col-lg-2, .col-xs-3, .col-sm-3, .col-md-3, .col-lg-3, .col-xs-4, .col-sm-4, .col-md-4, .col-lg-4, .col-xs-5, .col-sm-5, .col-md-5, .col-lg-5, .col-xs-6, .col-sm-6, .col-md-6, .col-lg-6, .col-xs-7, .col-sm-7, .col-md-7, .col-lg-7, .col-xs-8, .col-sm-8, .col-md-8, .col-lg-8, .col-xs-9, .col-sm-9, .col-md-9, .col-lg-9, .col-xs-10, .col-sm-10, .col-md-10, .col-lg-10, .col-xs-11, .col-sm-11, .col-md-11, .col-lg-11, .col-xs-12, .col-sm-12, .col-md-12, .col-lg-12 {
    position: relative;
    min-height: 1px;
    padding-right: 15px;
    padding-left: 15px;
  }
  .col-xs-1, .col-xs-2, .col-xs-3, .col-xs-4, .col-xs-5, .col-xs-6, .col-xs-7, .col-xs-8, .col-xs-9, .col-xs-10, .col-xs-11, .col-xs-12 {
    float: left;
  }
  .col-xs-12 {
    width: 100%;
  }
  .col-xs-11 {
    width: 91.66666667%;
  }
  .col-xs-10 {
    width: 83.33333333%;
  }
  .col-xs-9 {
    width: 75%;
  }
  .col-xs-8 {
    width: 66.66666667%;
  }
  .col-xs-7 {
    width: 58.33333333%;
  }
  .col-xs-6 {
    width: 50%;
  }
  .col-xs-5 {
    width: 41.66666667%;
  }
  .col-xs-4 {
    width: 33.33333333%;
  }
  .col-xs-3 {
    width: 25%;
  }
  .col-xs-2 {
    width: 16.66666667%;
  }
  .col-xs-1 {
    width: 8.33333333%;
  }
  .col-xs-pull-12 {
    right: 100%;
  }
  .col-xs-pull-11 {
    right: 91.66666667%;
  }
  .col-xs-pull-10 {
    right: 83.33333333%;
  }
  .col-xs-pull-9 {
    right: 75%;
  }
  .col-xs-pull-8 {
    right: 66.66666667%;
  }
  .col-xs-pull-7 {
    right: 58.33333333%;
  }
  .col-xs-pull-6 {
    right: 50%;
  }
  .col-xs-pull-5 {
    right: 41.66666667%;
  }
  .col-xs-pull-4 {
    right: 33.33333333%;
  }
  .col-xs-pull-3 {
    right: 25%;
  }
  .col-xs-pull-2 {
    right: 16.66666667%;
  }
  .col-xs-pull-1 {
    right: 8.33333333%;
  }
  .col-xs-pull-0 {
    right: auto;
  }
  .col-xs-push-12 {
    left: 100%;
  }
  .col-xs-push-11 {
    left: 91.66666667%;
  }
  .col-xs-push-10 {
    left: 83.33333333%;
  }
  .col-xs-push-9 {
    left: 75%;
  }
  .col-xs-push-8 {
    left: 66.66666667%;
  }
  .col-xs-push-7 {
    left: 58.33333333%;
  }
  .col-xs-push-6 {
    left: 50%;
  }
  .col-xs-push-5 {
    left: 41.66666667%;
  }
  .col-xs-push-4 {
    left: 33.33333333%;
  }
  .col-xs-push-3 {
    left: 25%;
  }
  .col-xs-push-2 {
    left: 16.66666667%;
  }
  .col-xs-push-1 {
    left: 8.33333333%;
  }
  .col-xs-push-0 {
    left: auto;
  }
  .col-xs-offset-12 {
    margin-left: 100%;
  }
  .col-xs-offset-11 {
    margin-left: 91.66666667%;
  }
  .col-xs-offset-10 {
    margin-left: 83.33333333%;
  }
  .col-xs-offset-9 {
    margin-left: 75%;
  }
  .col-xs-offset-8 {
    margin-left: 66.66666667%;
  }
  .col-xs-offset-7 {
    margin-left: 58.33333333%;
  }
  .col-xs-offset-6 {
    margin-left: 50%;
  }
  .col-xs-offset-5 {
    margin-left: 41.66666667%;
  }
  .col-xs-offset-4 {
    margin-left: 33.33333333%;
  }
  .col-xs-offset-3 {
    margin-left: 25%;
  }
  .col-xs-offset-2 {
    margin-left: 16.66666667%;
  }
  .col-xs-offset-1 {
    margin-left: 8.33333333%;
  }
  .col-xs-offset-0 {
    margin-left: 0;
  }
  @media (min-width: 768px) {
    .col-sm-1, .col-sm-2, .col-sm-3, .col-sm-4, .col-sm-5, .col-sm-6, .col-sm-7, .col-sm-8, .col-sm-9, .col-sm-10, .col-sm-11, .col-sm-12 {
      float: left;
    }
    .col-sm-12 {
      width: 100%;
    }
    .col-sm-11 {
      width: 91.66666667%;
    }
    .col-sm-10 {
      width: 83.33333333%;
    }
    .col-sm-9 {
      width: 75%;
    }
    .col-sm-8 {
      width: 66.66666667%;
    }
    .col-sm-7 {
      width: 58.33333333%;
    }
    .col-sm-6 {
      width: 50%;
    }
    .col-sm-5 {
      width: 41.66666667%;
    }
    .col-sm-4 {
      width: 33.33333333%;
    }
    .col-sm-3 {
      width: 25%;
    }
    .col-sm-2 {
      width: 16.66666667%;
    }
    .col-sm-1 {
      width: 8.33333333%;
    }
    .col-sm-pull-12 {
      right: 100%;
    }
    .col-sm-pull-11 {
      right: 91.66666667%;
    }
    .col-sm-pull-10 {
      right: 83.33333333%;
    }
    .col-sm-pull-9 {
      right: 75%;
    }
    .col-sm-pull-8 {
      right: 66.66666667%;
    }
    .col-sm-pull-7 {
      right: 58.33333333%;
    }
    .col-sm-pull-6 {
      right: 50%;
    }
    .col-sm-pull-5 {
      right: 41.66666667%;
    }
    .col-sm-pull-4 {
      right: 33.33333333%;
    }
    .col-sm-pull-3 {
      right: 25%;
    }
    .col-sm-pull-2 {
      right: 16.66666667%;
    }
    .col-sm-pull-1 {
      right: 8.33333333%;
    }
    .col-sm-pull-0 {
      right: auto;
    }
    .col-sm-push-12 {
      left: 100%;
    }
    .col-sm-push-11 {
      left: 91.66666667%;
    }
    .col-sm-push-10 {
      left: 83.33333333%;
    }
    .col-sm-push-9 {
      left: 75%;
    }
    .col-sm-push-8 {
      left: 66.66666667%;
    }
    .col-sm-push-7 {
      left: 58.33333333%;
    }
    .col-sm-push-6 {
      left: 50%;
    }
    .col-sm-push-5 {
      left: 41.66666667%;
    }
    .col-sm-push-4 {
      left: 33.33333333%;
    }
    .col-sm-push-3 {
      left: 25%;
    }
    .col-sm-push-2 {
      left: 16.66666667%;
    }
    .col-sm-push-1 {
      left: 8.33333333%;
    }
    .col-sm-push-0 {
      left: auto;
    }
    .col-sm-offset-12 {
      margin-left: 100%;
    }
    .col-sm-offset-11 {
      margin-left: 91.66666667%;
    }
    .col-sm-offset-10 {
      margin-left: 83.33333333%;
    }
    .col-sm-offset-9 {
      margin-left: 75%;
    }
    .col-sm-offset-8 {
      margin-left: 66.66666667%;
    }
    .col-sm-offset-7 {
      margin-left: 58.33333333%;
    }
    .col-sm-offset-6 {
      margin-left: 50%;
    }
    .col-sm-offset-5 {
      margin-left: 41.66666667%;
    }
    .col-sm-offset-4 {
      margin-left: 33.33333333%;
    }
    .col-sm-offset-3 {
      margin-left: 25%;
    }
    .col-sm-offset-2 {
      margin-left: 16.66666667%;
    }
    .col-sm-offset-1 {
      margin-left: 8.33333333%;
    }
    .col-sm-offset-0 {
      margin-left: 0;
    }
  }
  @media (min-width: 992px) {
    .col-md-1, .col-md-2, .col-md-3, .col-md-4, .col-md-5, .col-md-6, .col-md-7, .col-md-8, .col-md-9, .col-md-10, .col-md-11, .col-md-12 {
      float: left;
    }
    .col-md-12 {
      width: 100%;
    }
    .col-md-11 {
      width: 91.66666667%;
    }
    .col-md-10 {
      width: 83.33333333%;
    }
    .col-md-9 {
      width: 75%;
    }
    .col-md-8 {
      width: 66.66666667%;
    }
    .col-md-7 {
      width: 58.33333333%;
    }
    .col-md-6 {
      width: 50%;
    }
    .col-md-5 {
      width: 41.66666667%;
    }
    .col-md-4 {
      width: 33.33333333%;
    }
    .col-md-3 {
      width: 25%;
    }
    .col-md-2 {
      width: 16.66666667%;
    }
    .col-md-1 {
      width: 8.33333333%;
    }
    .col-md-pull-12 {
      right: 100%;
    }
    .col-md-pull-11 {
      right: 91.66666667%;
    }
    .col-md-pull-10 {
      right: 83.33333333%;
    }
    .col-md-pull-9 {
      right: 75%;
    }
    .col-md-pull-8 {
      right: 66.66666667%;
    }
    .col-md-pull-7 {
      right: 58.33333333%;
    }
    .col-md-pull-6 {
      right: 50%;
    }
    .col-md-pull-5 {
      right: 41.66666667%;
    }
    .col-md-pull-4 {
      right: 33.33333333%;
    }
    .col-md-pull-3 {
      right: 25%;
    }
    .col-md-pull-2 {
      right: 16.66666667%;
    }
    .col-md-pull-1 {
      right: 8.33333333%;
    }
    .col-md-pull-0 {
      right: auto;
    }
    .col-md-push-12 {
      left: 100%;
    }
    .col-md-push-11 {
      left: 91.66666667%;
    }
    .col-md-push-10 {
      left: 83.33333333%;
    }
    .col-md-push-9 {
      left: 75%;
    }
    .col-md-push-8 {
      left: 66.66666667%;
    }
    .col-md-push-7 {
      left: 58.33333333%;
    }
    .col-md-push-6 {
      left: 50%;
    }
    .col-md-push-5 {
      left: 41.66666667%;
    }
    .col-md-push-4 {
      left: 33.33333333%;
    }
    .col-md-push-3 {
      left: 25%;
    }
    .col-md-push-2 {
      left: 16.66666667%;
    }
    .col-md-push-1 {
      left: 8.33333333%;
    }
    .col-md-push-0 {
      left: auto;
    }
    .col-md-offset-12 {
      margin-left: 100%;
    }
    .col-md-offset-11 {
      margin-left: 91.66666667%;
    }
    .col-md-offset-10 {
      margin-left: 83.33333333%;
    }
    .col-md-offset-9 {
      margin-left: 75%;
    }
    .col-md-offset-8 {
      margin-left: 66.66666667%;
    }
    .col-md-offset-7 {
      margin-left: 58.33333333%;
    }
    .col-md-offset-6 {
      margin-left: 50%;
    }
    .col-md-offset-5 {
      margin-left: 41.66666667%;
    }
    .col-md-offset-4 {
      margin-left: 33.33333333%;
    }
    .col-md-offset-3 {
      margin-left: 25%;
    }
    .col-md-offset-2 {
      margin-left: 16.66666667%;
    }
    .col-md-offset-1 {
      margin-left: 8.33333333%;
    }
    .col-md-offset-0 {
      margin-left: 0;
    }
  }
  @media (min-width: 1200px) {
    .col-lg-1, .col-lg-2, .col-lg-3, .col-lg-4, .col-lg-5, .col-lg-6, .col-lg-7, .col-lg-8, .col-lg-9, .col-lg-10, .col-lg-11, .col-lg-12 {
      float: left;
    }
    .col-lg-12 {
      width: 100%;
    }
    .col-lg-11 {
      width: 91.66666667%;
    }
    .col-lg-10 {
      width: 83.33333333%;
    }
    .col-lg-9 {
      width: 75%;
    }
    .col-lg-8 {
      width: 66.66666667%;
    }
    .col-lg-7 {
      width: 58.33333333%;
    }
    .col-lg-6 {
      width: 50%;
    }
    .col-lg-5 {
      width: 41.66666667%;
    }
    .col-lg-4 {
      width: 33.33333333%;
    }
    .col-lg-3 {
      width: 25%;
    }
    .col-lg-2 {
      width: 16.66666667%;
    }
    .col-lg-1 {
      width: 8.33333333%;
    }
    .col-lg-pull-12 {
      right: 100%;
    }
    .col-lg-pull-11 {
      right: 91.66666667%;
    }
    .col-lg-pull-10 {
      right: 83.33333333%;
    }
    .col-lg-pull-9 {
      right: 75%;
    }
    .col-lg-pull-8 {
      right: 66.66666667%;
    }
    .col-lg-pull-7 {
      right: 58.33333333%;
    }
    .col-lg-pull-6 {
      right: 50%;
    }
    .col-lg-pull-5 {
      right: 41.66666667%;
    }
    .col-lg-pull-4 {
      right: 33.33333333%;
    }
    .col-lg-pull-3 {
      right: 25%;
    }
    .col-lg-pull-2 {
      right: 16.66666667%;
    }
    .col-lg-pull-1 {
      right: 8.33333333%;
    }
    .col-lg-pull-0 {
      right: auto;
    }
    .col-lg-push-12 {
      left: 100%;
    }
    .col-lg-push-11 {
      left: 91.66666667%;
    }
    .col-lg-push-10 {
      left: 83.33333333%;
    }
    .col-lg-push-9 {
      left: 75%;
    }
    .col-lg-push-8 {
      left: 66.66666667%;
    }
    .col-lg-push-7 {
      left: 58.33333333%;
    }
    .col-lg-push-6 {
      left: 50%;
    }
    .col-lg-push-5 {
      left: 41.66666667%;
    }
    .col-lg-push-4 {
      left: 33.33333333%;
    }
    .col-lg-push-3 {
      left: 25%;
    }
    .col-lg-push-2 {
      left: 16.66666667%;
    }
    .col-lg-push-1 {
      left: 8.33333333%;
    }
    .col-lg-push-0 {
      left: auto;
    }
    .col-lg-offset-12 {
      margin-left: 100%;
    }
    .col-lg-offset-11 {
      margin-left: 91.66666667%;
    }
    .col-lg-offset-10 {
      margin-left: 83.33333333%;
    }
    .col-lg-offset-9 {
      margin-left: 75%;
    }
    .col-lg-offset-8 {
      margin-left: 66.66666667%;
    }
    .col-lg-offset-7 {
      margin-left: 58.33333333%;
    }
    .col-lg-offset-6 {
      margin-left: 50%;
    }
    .col-lg-offset-5 {
      margin-left: 41.66666667%;
    }
    .col-lg-offset-4 {
      margin-left: 33.33333333%;
    }
    .col-lg-offset-3 {
      margin-left: 25%;
    }
    .col-lg-offset-2 {
      margin-left: 16.66666667%;
    }
    .col-lg-offset-1 {
      margin-left: 8.33333333%;
    }
    .col-lg-offset-0 {
      margin-left: 0;
    }
  }
  table {
    background-color: transparent;
  }
  caption {
    padding-top: 8px;
    padding-bottom: 8px;
    color: #8d99a6;
    text-align: left;
  }
  th {
    text-align: left;
  }
  .table {
    width: 100%;
    max-width: 100%;
    margin-bottom: 20px;
  }
  .table > thead > tr > th,
  .table > tbody > tr > th,
  .table > tfoot > tr > th,
  .table > thead > tr > td,
  .table > tbody > tr > td,
  .table > tfoot > tr > td {
    padding: 8px;
    line-height: 1.42857143;
    vertical-align: top;
    border-top: 1px solid #d1d8dd;
  }
  .table > thead > tr > th {
    vertical-align: bottom;
    border-bottom: 2px solid #d1d8dd;
  }
  .table > caption + thead > tr:first-child > th,
  .table > colgroup + thead > tr:first-child > th,
  .table > thead:first-child > tr:first-child > th,
  .table > caption + thead > tr:first-child > td,
  .table > colgroup + thead > tr:first-child > td,
  .table > thead:first-child > tr:first-child > td {
    border-top: 0;
  }
  .table > tbody + tbody {
    border-top: 2px solid #d1d8dd;
  }
  .table .table {
    background-color: #fff;
  }
  .table-condensed > thead > tr > th,
  .table-condensed > tbody > tr > th,
  .table-condensed > tfoot > tr > th,
  .table-condensed > thead > tr > td,
  .table-condensed > tbody > tr > td,
  .table-condensed > tfoot > tr > td {
    padding: 5px;
  }
  .table-bordered {
    border: 1px solid #d1d8dd;
  }
  .table-bordered > thead > tr > th,
  .table-bordered > tbody > tr > th,
  .table-bordered > tfoot > tr > th,
  .table-bordered > thead > tr > td,
  .table-bordered > tbody > tr > td,
  .table-bordered > tfoot > tr > td {
    border: 1px solid #d1d8dd;
  }
  .table-bordered > thead > tr > th,
  .table-bordered > thead > tr > td {
    border-bottom-width: 2px;
  }
  .table-striped > tbody > tr:nth-child(odd) {
    background-color: #f9f9f9;
  }
  .table-hover > tbody > tr:hover {
    background-color: #f5f5f5;
  }
  table col[class*='col-'] {
    position: static;
    display: table-column;
    float: none;
  }
  table td[class*='col-'],
  table th[class*='col-'] {
    position: static;
    display: table-cell;
    float: none;
  }
  .table > thead > tr > td.active,
  .table > tbody > tr > td.active,
  .table > tfoot > tr > td.active,
  .table > thead > tr > th.active,
  .table > tbody > tr > th.active,
  .table > tfoot > tr > th.active,
  .table > thead > tr.active > td,
  .table > tbody > tr.active > td,
  .table > tfoot > tr.active > td,
  .table > thead > tr.active > th,
  .table > tbody > tr.active > th,
  .table > tfoot > tr.active > th {
    background-color: #f5f5f5;
  }
  .table-hover > tbody > tr > td.active:hover,
  .table-hover > tbody > tr > th.active:hover,
  .table-hover > tbody > tr.active:hover > td,
  .table-hover > tbody > tr:hover > .active,
  .table-hover > tbody > tr.active:hover > th {
    background-color: #e8e8e8;
  }
  .table > thead > tr > td.success,
  .table > tbody > tr > td.success,
  .table > tfoot > tr > td.success,
  .table > thead > tr > th.success,
  .table > tbody > tr > th.success,
  .table > tfoot > tr > th.success,
  .table > thead > tr.success > td,
  .table > tbody > tr.success > td,
  .table > tfoot > tr.success > td,
  .table > thead > tr.success > th,
  .table > tbody > tr.success > th,
  .table > tfoot > tr.success > th {
    background-color: transparent;
  }
  .table-hover > tbody > tr > td.success:hover,
  .table-hover > tbody > tr > th.success:hover,
  .table-hover > tbody > tr.success:hover > td,
  .table-hover > tbody > tr:hover > .success,
  .table-hover > tbody > tr.success:hover > th {
    background-color: rgba(0, 0, 0, 0);
  }
  .table > thead > tr > td.info,
  .table > tbody > tr > td.info,
  .table > tfoot > tr > td.info,
  .table > thead > tr > th.info,
  .table > tbody > tr > th.info,
  .table > tfoot > tr > th.info,
  .table > thead > tr.info > td,
  .table > tbody > tr.info > td,
  .table > tfoot > tr.info > td,
  .table > thead > tr.info > th,
  .table > tbody > tr.info > th,
  .table > tfoot > tr.info > th {
    background-color: transparent;
  }
  .table-hover > tbody > tr > td.info:hover,
  .table-hover > tbody > tr > th.info:hover,
  .table-hover > tbody > tr.info:hover > td,
  .table-hover > tbody > tr:hover > .info,
  .table-hover > tbody > tr.info:hover > th {
    background-color: rgba(0, 0, 0, 0);
  }
  .table > thead > tr > td.warning,
  .table > tbody > tr > td.warning,
  .table > tfoot > tr > td.warning,
  .table > thead > tr > th.warning,
  .table > tbody > tr > th.warning,
  .table > tfoot > tr > th.warning,
  .table > thead > tr.warning > td,
  .table > tbody > tr.warning > td,
  .table > tfoot > tr.warning > td,
  .table > thead > tr.warning > th,
  .table > tbody > tr.warning > th,
  .table > tfoot > tr.warning > th {
    background-color: transparent;
  }
  .table-hover > tbody > tr > td.warning:hover,
  .table-hover > tbody > tr > th.warning:hover,
  .table-hover > tbody > tr.warning:hover > td,
  .table-hover > tbody > tr:hover > .warning,
  .table-hover > tbody > tr.warning:hover > th {
    background-color: rgba(0, 0, 0, 0);
  }
  .table > thead > tr > td.danger,
  .table > tbody > tr > td.danger,
  .table > tfoot > tr > td.danger,
  .table > thead > tr > th.danger,
  .table > tbody > tr > th.danger,
  .table > tfoot > tr > th.danger,
  .table > thead > tr.danger > td,
  .table > tbody > tr.danger > td,
  .table > tfoot > tr.danger > td,
  .table > thead > tr.danger > th,
  .table > tbody > tr.danger > th,
  .table > tfoot > tr.danger > th {
    background-color: transparent;
  }
  .table-hover > tbody > tr > td.danger:hover,
  .table-hover > tbody > tr > th.danger:hover,
  .table-hover > tbody > tr.danger:hover > td,
  .table-hover > tbody > tr:hover > .danger,
  .table-hover > tbody > tr.danger:hover > th {
    background-color: rgba(0, 0, 0, 0);
  }
  .table-responsive {
    min-height: .01%;
    overflow-x: auto;
  }
  @media screen and (max-width: 767px) {
    .table-responsive {
      width: 100%;
      margin-bottom: 15px;
      overflow-y: hidden;
      -ms-overflow-style: -ms-autohiding-scrollbar;
      border: 1px solid #d1d8dd;
    }
    .table-responsive > .table {
      margin-bottom: 0;
    }
    .table-responsive > .table > thead > tr > th,
    .table-responsive > .table > tbody > tr > th,
    .table-responsive > .table > tfoot > tr > th,
    .table-responsive > .table > thead > tr > td,
    .table-responsive > .table > tbody > tr > td,
    .table-responsive > .table > tfoot > tr > td {
      white-space: nowrap;
    }
    .table-responsive > .table-bordered {
      border: 0;
    }
    .table-responsive > .table-bordered > thead > tr > th:first-child,
    .table-responsive > .table-bordered > tbody > tr > th:first-child,
    .table-responsive > .table-bordered > tfoot > tr > th:first-child,
    .table-responsive > .table-bordered > thead > tr > td:first-child,
    .table-responsive > .table-bordered > tbody > tr > td:first-child,
    .table-responsive > .table-bordered > tfoot > tr > td:first-child {
      border-left: 0;
    }
    .table-responsive > .table-bordered > thead > tr > th:last-child,
    .table-responsive > .table-bordered > tbody > tr > th:last-child,
    .table-responsive > .table-bordered > tfoot > tr > th:last-child,
    .table-responsive > .table-bordered > thead > tr > td:last-child,
    .table-responsive > .table-bordered > tbody > tr > td:last-child,
    .table-responsive > .table-bordered > tfoot > tr > td:last-child {
      border-right: 0;
    }
    .table-responsive > .table-bordered > tbody > tr:last-child > th,
    .table-responsive > .table-bordered > tfoot > tr:last-child > th,
    .table-responsive > .table-bordered > tbody > tr:last-child > td,
    .table-responsive > .table-bordered > tfoot > tr:last-child > td {
      border-bottom: 0;
    }
  }
  fieldset {
    min-width: 0;
    padding: 0;
    margin: 0;
    border: 0;
  }
  legend {
    display: block;
    width: 100%;
    padding: 0;
    margin-bottom: 20px;
    font-size: 21px;
    line-height: inherit;
    color: #333;
    border: 0;
    border-bottom: 1px solid #e5e5e5;
  }
  label {
    display: inline-block;
    max-width: 100%;
    margin-bottom: 5px;
    font-weight: bold;
  }
  input[type='search'] {
    -webkit-box-sizing: border-box;
       -moz-box-sizing: border-box;
            box-sizing: border-box;
  }
  input[type='radio'],
  input[type='checkbox'] {
    margin: 4px 0 0;
    margin-top: 1px;
    line-height: normal;
  }
  input[type='file'] {
    display: block;
  }
  input[type='range'] {
    display: block;
    width: 100%;
  }
  select[multiple],
  select[size] {
    height: auto;
  }
  input[type='file']:focus,
  input[type='radio']:focus,
  input[type='checkbox']:focus {
    outline: thin dotted;
    outline: 5px auto -webkit-focus-ring-color;
    outline-offset: -2px;
  }
  output {
    display: block;
    padding-top: 5px;
    font-size: 14px;
    line-height: 1.42857143;
    color: #555;
  }
  .form-control {
    display: block;
    width: 100%;
    height: 30px;
    padding: 4px 10px;
    font-size: 14px;
    line-height: 1.42857143;
    color: #555;
    background-color: #fff;
    background-image: none;
    border: 1px solid #d1d8dd;
    border-radius: 4px;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075);
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075);
    -webkit-transition: border-color ease-in-out .15s, -webkit-box-shadow ease-in-out .15s;
         -o-transition: border-color ease-in-out .15s, box-shadow ease-in-out .15s;
            transition: border-color ease-in-out .15s, box-shadow ease-in-out .15s;
  }
  .form-control:focus {
    border-color: #ced5db;
    outline: 0;
    -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px rgba(206, 213, 219, .6);
            box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px rgba(206, 213, 219, .6);
  }
  .form-control:focus {
    border-color: #ced5db;
    outline: 0;
    -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 3px rgba(206, 213, 219, .6);
            box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 3px rgba(206, 213, 219, .6);
  }
  .form-control::-moz-placeholder {
    color: #d1d8dd;
    opacity: 1;
  }
  .form-control:-ms-input-placeholder {
    color: #d1d8dd;
  }
  .form-control::-webkit-input-placeholder {
    color: #d1d8dd;
  }
  .form-control[disabled],
  .form-control[readonly],
  fieldset[disabled] .form-control {
    cursor: not-allowed;
    background-color: #eee;
    opacity: 1;
  }
  textarea.form-control {
    height: auto;
  }
  input[type='search'] {
    -webkit-appearance: none;
  }
  @media screen and (-webkit-min-device-pixel-ratio: 0) {
    input[type='date'],
    input[type='time'],
    input[type='datetime-local'],
    input[type='month'] {
      line-height: 30px;
    }
    input[type='date'].input-sm,
    input[type='time'].input-sm,
    input[type='datetime-local'].input-sm,
    input[type='month'].input-sm,
    .input-group-sm input[type='date'],
    .input-group-sm input[type='time'],
    .input-group-sm input[type='datetime-local'],
    .input-group-sm input[type='month'] {
      line-height: 30px;
    }
    input[type='date'].input-lg,
    input[type='time'].input-lg,
    input[type='datetime-local'].input-lg,
    input[type='month'].input-lg,
    .input-group-lg input[type='date'],
    .input-group-lg input[type='time'],
    .input-group-lg input[type='datetime-local'],
    .input-group-lg input[type='month'] {
      line-height: 46px;
    }
  }
  .form-group {
    margin-bottom: 15px;
  }
  .radio,
  .checkbox {
    position: relative;
    display: block;
    margin-top: 10px;
    margin-bottom: 10px;
  }
  .radio label,
  .checkbox label {
    min-height: 20px;
    padding-left: 20px;
    margin-bottom: 0;
    font-weight: normal;
    cursor: pointer;
  }
  .radio input[type='radio'],
  .radio-inline input[type='radio'],
  .checkbox input[type='checkbox'],
  .checkbox-inline input[type='checkbox'] {
    position: absolute;
    margin-top: 4px 9;
    margin-left: -20px;
  }
  .radio + .radio,
  .checkbox + .checkbox {
    margin-top: -5px;
  }
  .radio-inline,
  .checkbox-inline {
    display: inline-block;
    padding-left: 20px;
    margin-bottom: 0;
    font-weight: normal;
    vertical-align: middle;
    cursor: pointer;
  }
  .radio-inline + .radio-inline,
  .checkbox-inline + .checkbox-inline {
    margin-top: 0;
    margin-left: 10px;
  }
  input[type='radio'][disabled],
  input[type='checkbox'][disabled],
  input[type='radio'].disabled,
  input[type='checkbox'].disabled,
  fieldset[disabled] input[type='radio'],
  fieldset[disabled] input[type='checkbox'] {
    cursor: not-allowed;
  }
  .radio-inline.disabled,
  .checkbox-inline.disabled,
  fieldset[disabled] .radio-inline,
  fieldset[disabled] .checkbox-inline {
    cursor: not-allowed;
  }
  .radio.disabled label,
  .checkbox.disabled label,
  fieldset[disabled] .radio label,
  fieldset[disabled] .checkbox label {
    cursor: not-allowed;
  }
  .form-control-static {
    padding-top: 5px;
    padding-bottom: 5px;
    margin-bottom: 0;
  }
  .form-control-static.input-lg,
  .form-control-static.input-sm {
    padding-right: 0;
    padding-left: 0;
  }
  .input-sm {
    height: 30px;
    padding: 5px 10px;
    font-size: 12px;
    line-height: 1.5;
    border-radius: 3px;
  }
  select.input-sm {
    height: 30px;
    line-height: 30px;
  }
  textarea.input-sm,
  select[multiple].input-sm {
    height: auto;
  }
  .form-group-sm .form-control {
    height: 30px;
    padding: 5px 10px;
    font-size: 12px;
    line-height: 1.5;
    border-radius: 3px;
  }
  select.form-group-sm .form-control {
    height: 30px;
    line-height: 30px;
  }
  textarea.form-group-sm .form-control,
  select[multiple].form-group-sm .form-control {
    height: auto;
  }
  .input-lg {
    height: 46px;
    padding: 10px 16px;
    font-size: 18px;
    line-height: 1.33;
    border-radius: 6px;
  }
  select.input-lg {
    height: 46px;
    line-height: 46px;
  }
  textarea.input-lg,
  select[multiple].input-lg {
    height: auto;
  }
  .form-group-lg .form-control {
    height: 46px;
    padding: 10px 16px;
    font-size: 18px;
    line-height: 1.33;
    border-radius: 6px;
  }
  select.form-group-lg .form-control {
    height: 46px;
    line-height: 46px;
  }
  textarea.form-group-lg .form-control,
  select[multiple].form-group-lg .form-control {
    height: auto;
  }
  .has-feedback {
    position: relative;
  }
  .has-feedback .form-control {
    padding-right: 37.5px;
  }
  .form-control-feedback {
    position: absolute;
    top: 0;
    right: 0;
    z-index: 2;
    display: block;
    width: 30px;
    height: 30px;
    line-height: 30px;
    text-align: center;
    pointer-events: none;
  }
  .input-lg + .form-control-feedback {
    width: 46px;
    height: 46px;
    line-height: 46px;
  }
  .input-sm + .form-control-feedback {
    width: 30px;
    height: 30px;
    line-height: 30px;
  }
  .has-success .help-block,
  .has-success .control-label,
  .has-success .radio,
  .has-success .checkbox,
  .has-success .radio-inline,
  .has-success .checkbox-inline,
  .has-success.radio label,
  .has-success.checkbox label,
  .has-success.radio-inline label,
  .has-success.checkbox-inline label {
    color: #98d85b;
  }
  .has-success .form-control {
    border-color: #98d85b;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075);
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075);
  }
  .has-success .form-control:focus {
    border-color: #7ece32;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075), 0 0 6px #ccecad;
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075), 0 0 6px #ccecad;
  }
  .has-success .input-group-addon {
    color: #98d85b;
    background-color: transparent;
    border-color: #98d85b;
  }
  .has-success .form-control-feedback {
    color: #98d85b;
  }
  .has-warning .help-block,
  .has-warning .control-label,
  .has-warning .radio,
  .has-warning .checkbox,
  .has-warning .radio-inline,
  .has-warning .checkbox-inline,
  .has-warning.radio label,
  .has-warning.checkbox label,
  .has-warning.radio-inline label,
  .has-warning.checkbox-inline label {
    color: #ffa00a;
  }
  .has-warning .form-control {
    border-color: #ffa00a;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075);
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075);
  }
  .has-warning .form-control:focus {
    border-color: #d68300;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075), 0 0 6px #ffc870;
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075), 0 0 6px #ffc870;
  }
  .has-warning .input-group-addon {
    color: #ffa00a;
    background-color: transparent;
    border-color: #ffa00a;
  }
  .has-warning .form-control-feedback {
    color: #ffa00a;
  }
  .has-error .help-block,
  .has-error .control-label,
  .has-error .radio,
  .has-error .checkbox,
  .has-error .radio-inline,
  .has-error .checkbox-inline,
  .has-error.radio label,
  .has-error.checkbox label,
  .has-error.radio-inline label,
  .has-error.checkbox-inline label {
    color: #ff5858;
  }
  .has-error .form-control {
    border-color: #ff5858;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075);
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075);
  }
  .has-error .form-control:focus {
    border-color: #ff2525;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075), 0 0 6px #ffbebe;
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075), 0 0 6px #ffbebe;
  }
  .has-error .input-group-addon {
    color: #ff5858;
    background-color: transparent;
    border-color: #ff5858;
  }
  .has-error .form-control-feedback {
    color: #ff5858;
  }
  .has-feedback label ~ .form-control-feedback {
    top: 25px;
  }
  .has-feedback label.sr-only ~ .form-control-feedback {
    top: 0;
  }
  .help-block {
    display: block;
    margin-top: 5px;
    margin-bottom: 10px;
    color: #6b8196;
  }
  @media (min-width: 768px) {
    .form-inline .form-group {
      display: inline-block;
      margin-bottom: 0;
      vertical-align: middle;
    }
    .form-inline .form-control {
      display: inline-block;
      width: auto;
      vertical-align: middle;
    }
    .form-inline .form-control-static {
      display: inline-block;
    }
    .form-inline .input-group {
      display: inline-table;
      vertical-align: middle;
    }
    .form-inline .input-group .input-group-addon,
    .form-inline .input-group .input-group-btn,
    .form-inline .input-group .form-control {
      width: auto;
    }
    .form-inline .input-group > .form-control {
      width: 100%;
    }
    .form-inline .control-label {
      margin-bottom: 0;
      vertical-align: middle;
    }
    .form-inline .radio,
    .form-inline .checkbox {
      display: inline-block;
      margin-top: 0;
      margin-bottom: 0;
      vertical-align: middle;
    }
    .form-inline .radio label,
    .form-inline .checkbox label {
      padding-left: 0;
    }
    .form-inline .radio input[type='radio'],
    .form-inline .checkbox input[type='checkbox'] {
      position: relative;
      margin-left: 0;
    }
    .form-inline .has-feedback .form-control-feedback {
      top: 0;
    }
  }
  .form-horizontal .radio,
  .form-horizontal .checkbox,
  .form-horizontal .radio-inline,
  .form-horizontal .checkbox-inline {
    padding-top: 5px;
    margin-top: 0;
    margin-bottom: 0;
  }
  .form-horizontal .radio,
  .form-horizontal .checkbox {
    min-height: 25px;
  }
  .form-horizontal .form-group {
    margin-right: -15px;
    margin-left: -15px;
  }
  @media (min-width: 768px) {
    .form-horizontal .control-label {
      padding-top: 5px;
      margin-bottom: 0;
      text-align: right;
    }
  }
  .form-horizontal .has-feedback .form-control-feedback {
    right: 15px;
  }
  @media (min-width: 768px) {
    .form-horizontal .form-group-lg .control-label {
      padding-top: 14.3px;
    }
  }
  @media (min-width: 768px) {
    .form-horizontal .form-group-sm .control-label {
      padding-top: 6px;
    }
  }
  .btn {
    display: inline-block;
    padding: 4px 10px;
    margin-bottom: 0;
    font-size: 14px;
    font-weight: normal;
    line-height: 1.42857143;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    -ms-touch-action: manipulation;
        touch-action: manipulation;
    cursor: pointer;
    -webkit-user-select: none;
       -moz-user-select: none;
        -ms-user-select: none;
            user-select: none;
    background-image: none;
    border: 1px solid transparent;
    border-radius: 4px;
  }
  .btn:focus,
  .btn:active:focus,
  .btn.active:focus,
  .btn.focus,
  .btn:active.focus,
  .btn.active.focus {
    outline: thin dotted;
    outline: 5px auto -webkit-focus-ring-color;
    outline-offset: -2px;
  }
  .btn:hover,
  .btn:focus,
  .btn.focus {
    color: inherit;
    text-decoration: none;
  }
  .btn:active,
  .btn.active {
    background-image: none;
    outline: 0;
    -webkit-box-shadow: inset 0 3px 5px rgba(0, 0, 0, .125);
            box-shadow: inset 0 3px 5px rgba(0, 0, 0, .125);
  }
  .btn.disabled,
  .btn[disabled],
  fieldset[disabled] .btn {
    pointer-events: none;
    cursor: not-allowed;
    filter: alpha(opacity=65);
    -webkit-box-shadow: none;
            box-shadow: none;
    opacity: .65;
  }
  .btn-default {
    color: inherit;
    background-color: #f0f4f7;
    border-color: transparent;
  }
  .btn-default:hover,
  .btn-default:focus,
  .btn-default.focus,
  .btn-default:active,
  .btn-default.active,
  .open > .dropdown-toggle.btn-default {
    color: inherit;
    background-color: #cfdce5;
    border-color: rgba(0, 0, 0, 0);
  }
  .btn-default:active,
  .btn-default.active,
  .open > .dropdown-toggle.btn-default {
    background-image: none;
  }
  .btn-default.disabled,
  .btn-default[disabled],
  fieldset[disabled] .btn-default,
  .btn-default.disabled:hover,
  .btn-default[disabled]:hover,
  fieldset[disabled] .btn-default:hover,
  .btn-default.disabled:focus,
  .btn-default[disabled]:focus,
  fieldset[disabled] .btn-default:focus,
  .btn-default.disabled.focus,
  .btn-default[disabled].focus,
  fieldset[disabled] .btn-default.focus,
  .btn-default.disabled:active,
  .btn-default[disabled]:active,
  fieldset[disabled] .btn-default:active,
  .btn-default.disabled.active,
  .btn-default[disabled].active,
  fieldset[disabled] .btn-default.active {
    background-color: #f0f4f7;
    border-color: transparent;
  }
  .btn-default .badge {
    color: #f0f4f7;
    background-color: inherit;
  }
  .btn-primary {
    color: #fff;
    background-color: #5e64ff;
    border-color: #444bff;
  }
  .btn-primary:hover,
  .btn-primary:focus,
  .btn-primary.focus,
  .btn-primary:active,
  .btn-primary.active,
  .open > .dropdown-toggle.btn-primary {
    color: #fff;
    background-color: #2b33ff;
    border-color: #0711ff;
  }
  .btn-primary:active,
  .btn-primary.active,
  .open > .dropdown-toggle.btn-primary {
    background-image: none;
  }
  .btn-primary.disabled,
  .btn-primary[disabled],
  fieldset[disabled] .btn-primary,
  .btn-primary.disabled:hover,
  .btn-primary[disabled]:hover,
  fieldset[disabled] .btn-primary:hover,
  .btn-primary.disabled:focus,
  .btn-primary[disabled]:focus,
  fieldset[disabled] .btn-primary:focus,
  .btn-primary.disabled.focus,
  .btn-primary[disabled].focus,
  fieldset[disabled] .btn-primary.focus,
  .btn-primary.disabled:active,
  .btn-primary[disabled]:active,
  fieldset[disabled] .btn-primary:active,
  .btn-primary.disabled.active,
  .btn-primary[disabled].active,
  fieldset[disabled] .btn-primary.active {
    background-color: #5e64ff;
    border-color: #444bff;
  }
  .btn-primary .badge {
    color: #5e64ff;
    background-color: #fff;
  }
  .btn-success {
    color: #fff;
    background-color: #98d85b;
    border-color: #8bd346;
  }
  .btn-success:hover,
  .btn-success:focus,
  .btn-success.focus,
  .btn-success:active,
  .btn-success.active,
  .open > .dropdown-toggle.btn-success {
    color: #fff;
    background-color: #7ece32;
    border-color: #6db22a;
  }
  .btn-success:active,
  .btn-success.active,
  .open > .dropdown-toggle.btn-success {
    background-image: none;
  }
  .btn-success.disabled,
  .btn-success[disabled],
  fieldset[disabled] .btn-success,
  .btn-success.disabled:hover,
  .btn-success[disabled]:hover,
  fieldset[disabled] .btn-success:hover,
  .btn-success.disabled:focus,
  .btn-success[disabled]:focus,
  fieldset[disabled] .btn-success:focus,
  .btn-success.disabled.focus,
  .btn-success[disabled].focus,
  fieldset[disabled] .btn-success.focus,
  .btn-success.disabled:active,
  .btn-success[disabled]:active,
  fieldset[disabled] .btn-success:active,
  .btn-success.disabled.active,
  .btn-success[disabled].active,
  fieldset[disabled] .btn-success.active {
    background-color: #98d85b;
    border-color: #8bd346;
  }
  .btn-success .badge {
    color: #98d85b;
    background-color: #fff;
  }
  .btn-info {
    color: #fff;
    background-color: #8d99a6;
    border-color: #7f8c9b;
  }
  .btn-info:hover,
  .btn-info:focus,
  .btn-info.focus,
  .btn-info:active,
  .btn-info.active,
  .open > .dropdown-toggle.btn-info {
    color: #fff;
    background-color: #707f90;
    border-color: #616e7c;
  }
  .btn-info:active,
  .btn-info.active,
  .open > .dropdown-toggle.btn-info {
    background-image: none;
  }
  .btn-info.disabled,
  .btn-info[disabled],
  fieldset[disabled] .btn-info,
  .btn-info.disabled:hover,
  .btn-info[disabled]:hover,
  fieldset[disabled] .btn-info:hover,
  .btn-info.disabled:focus,
  .btn-info[disabled]:focus,
  fieldset[disabled] .btn-info:focus,
  .btn-info.disabled.focus,
  .btn-info[disabled].focus,
  fieldset[disabled] .btn-info.focus,
  .btn-info.disabled:active,
  .btn-info[disabled]:active,
  fieldset[disabled] .btn-info:active,
  .btn-info.disabled.active,
  .btn-info[disabled].active,
  fieldset[disabled] .btn-info.active {
    background-color: #8d99a6;
    border-color: #7f8c9b;
  }
  .btn-info .badge {
    color: #8d99a6;
    background-color: #fff;
  }
  .btn-warning {
    color: #fff;
    background-color: #ffa00a;
    border-color: #f09300;
  }
  .btn-warning:hover,
  .btn-warning:focus,
  .btn-warning.focus,
  .btn-warning:active,
  .btn-warning.active,
  .open > .dropdown-toggle.btn-warning {
    color: #fff;
    background-color: #d68300;
    border-color: #b26d00;
  }
  .btn-warning:active,
  .btn-warning.active,
  .open > .dropdown-toggle.btn-warning {
    background-image: none;
  }
  .btn-warning.disabled,
  .btn-warning[disabled],
  fieldset[disabled] .btn-warning,
  .btn-warning.disabled:hover,
  .btn-warning[disabled]:hover,
  fieldset[disabled] .btn-warning:hover,
  .btn-warning.disabled:focus,
  .btn-warning[disabled]:focus,
  fieldset[disabled] .btn-warning:focus,
  .btn-warning.disabled.focus,
  .btn-warning[disabled].focus,
  fieldset[disabled] .btn-warning.focus,
  .btn-warning.disabled:active,
  .btn-warning[disabled]:active,
  fieldset[disabled] .btn-warning:active,
  .btn-warning.disabled.active,
  .btn-warning[disabled].active,
  fieldset[disabled] .btn-warning.active {
    background-color: #ffa00a;
    border-color: #f09300;
  }
  .btn-warning .badge {
    color: #ffa00a;
    background-color: #fff;
  }
  .btn-danger {
    color: #fff;
    background-color: #ff5858;
    border-color: #ff3f3f;
  }
  .btn-danger:hover,
  .btn-danger:focus,
  .btn-danger.focus,
  .btn-danger:active,
  .btn-danger.active,
  .open > .dropdown-toggle.btn-danger {
    color: #fff;
    background-color: #ff2525;
    border-color: #ff0101;
  }
  .btn-danger:active,
  .btn-danger.active,
  .open > .dropdown-toggle.btn-danger {
    background-image: none;
  }
  .btn-danger.disabled,
  .btn-danger[disabled],
  fieldset[disabled] .btn-danger,
  .btn-danger.disabled:hover,
  .btn-danger[disabled]:hover,
  fieldset[disabled] .btn-danger:hover,
  .btn-danger.disabled:focus,
  .btn-danger[disabled]:focus,
  fieldset[disabled] .btn-danger:focus,
  .btn-danger.disabled.focus,
  .btn-danger[disabled].focus,
  fieldset[disabled] .btn-danger.focus,
  .btn-danger.disabled:active,
  .btn-danger[disabled]:active,
  fieldset[disabled] .btn-danger:active,
  .btn-danger.disabled.active,
  .btn-danger[disabled].active,
  fieldset[disabled] .btn-danger.active {
    background-color: #ff5858;
    border-color: #ff3f3f;
  }
  .btn-danger .badge {
    color: #ff5858;
    background-color: #fff;
  }
  .btn-link {
    font-weight: normal;
    color: #36414c;
    border-radius: 0;
  }
  .btn-link,
  .btn-link:active,
  .btn-link.active,
  .btn-link[disabled],
  fieldset[disabled] .btn-link {
    background-color: transparent;
    -webkit-box-shadow: none;
            box-shadow: none;
  }
  .btn-link,
  .btn-link:hover,
  .btn-link:focus,
  .btn-link:active {
    border-color: transparent;
  }
  .btn-link:hover,
  .btn-link:focus {
    color: #161b1f;
    text-decoration: underline;
    background-color: transparent;
  }
  .btn-link[disabled]:hover,
  fieldset[disabled] .btn-link:hover,
  .btn-link[disabled]:focus,
  fieldset[disabled] .btn-link:focus {
    color: #777;
    text-decoration: none;
  }
  .btn-lg,
  .btn-group-lg > .btn {
    padding: 10px 16px;
    font-size: 18px;
    line-height: 1.33;
    border-radius: 6px;
  }
  .btn-sm,
  .btn-group-sm > .btn {
    padding: 5px 10px;
    font-size: 12px;
    line-height: 1.5;
    border-radius: 3px;
  }
  .btn-xs,
  .btn-group-xs > .btn {
    padding: 1px 5px;
    font-size: 12px;
    line-height: 1.5;
    border-radius: 3px;
  }
  .btn-block {
    display: block;
    width: 100%;
  }
  .btn-block + .btn-block {
    margin-top: 5px;
  }
  input[type='submit'].btn-block,
  input[type='reset'].btn-block,
  input[type='button'].btn-block {
    width: 100%;
  }
  .fade {
    opacity: 0;
    -webkit-transition: opacity .15s linear;
         -o-transition: opacity .15s linear;
            transition: opacity .15s linear;
  }
  .fade.in {
    opacity: 1;
  }
  .collapse {
    display: none;
    visibility: hidden;
  }
  .collapse.in {
    display: block;
    visibility: visible;
  }
  tr.collapse.in {
    display: table-row;
  }
  tbody.collapse.in {
    display: table-row-group;
  }
  .collapsing {
    position: relative;
    height: 0;
    overflow: hidden;
    -webkit-transition-timing-function: ease;
         -o-transition-timing-function: ease;
            transition-timing-function: ease;
    -webkit-transition-duration: .35s;
         -o-transition-duration: .35s;
            transition-duration: .35s;
    -webkit-transition-property: height, visibility;
         -o-transition-property: height, visibility;
            transition-property: height, visibility;
  }
  .caret {
    display: inline-block;
    width: 0;
    height: 0;
    margin-left: 2px;
    vertical-align: middle;
    border-top: 4px solid;
    border-right: 4px solid transparent;
    border-left: 4px solid transparent;
  }
  .dropdown {
    position: relative;
  }
  .dropdown-toggle:focus {
    outline: 0;
  }
  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 1000;
    display: none;
    float: left;
    min-width: 160px;
    padding: 5px 0;
    margin: 2px 0 0;
    font-size: 14px;
    text-align: left;
    list-style: none;
    background-color: #fff;
    -webkit-background-clip: padding-box;
            background-clip: padding-box;
    border: 1px solid #ccc;
    border: 1px solid rgba(0, 0, 0, .15);
    border-radius: 4px;
    -webkit-box-shadow: 0px 0px 1px rgba(0,0,0,0.200), 0px 1px 3px rgba(0,0,0,0.050), 0px 10px 24px -3px rgba(0,0,0,0.100);
            box-shadow: 0px 0px 1px rgba(0,0,0,0.200), 0px 1px 3px rgba(0,0,0,0.050), 0px 10px 24px -3px rgba(0,0,0,0.100);
  }
  .dropdown-menu.pull-right {
    right: 0;
    left: auto;
  }
  .dropdown-menu .divider {
    height: 1px;
    margin: 9px 0;
    overflow: hidden;
    background-color: #d8dfe5;
  }
  .dropdown-menu > li > a {
    display: block;
    padding: 3px 20px;
    clear: both;
    font-weight: normal;
    line-height: 1.42857143;
    color: #333;
    white-space: nowrap;
  }
  .dropdown-menu > li > a:hover,
  .dropdown-menu > li > a:focus {
    color: #262626;
    text-decoration: none;
    background-color: #f0f4f7;
  }
  .dropdown-menu > .active > a,
  .dropdown-menu > .active > a:hover,
  .dropdown-menu > .active > a:focus {
    color: inherit;
    text-decoration: none;
    background-color: #f0f4f7;
    outline: 0;
  }
  .dropdown-menu > .disabled > a,
  .dropdown-menu > .disabled > a:hover,
  .dropdown-menu > .disabled > a:focus {
    color: #777;
  }
  .dropdown-menu > .disabled > a:hover,
  .dropdown-menu > .disabled > a:focus {
    text-decoration: none;
    cursor: not-allowed;
    background-color: transparent;
    background-image: none;
    filter: progid:DXImageTransform.Microsoft.gradient(enabled = false);
  }
  .open > .dropdown-menu {
    display: block;
  }
  .open > a {
    outline: 0;
  }
  .dropdown-menu-right {
    right: 0;
    left: auto;
  }
  .dropdown-menu-left {
    right: auto;
    left: 0;
  }
  .dropdown-header {
    display: block;
    padding: 3px 20px;
    font-size: 12px;
    line-height: 1.42857143;
    color: #777;
    white-space: nowrap;
  }
  .dropdown-backdrop {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 99;
  }
  .pull-right > .dropdown-menu {
    right: 0;
    left: auto;
  }
  .dropup .caret,
  .navbar-fixed-bottom .dropdown .caret {
    content: '';
    border-top: 0;
    border-bottom: 4px solid;
  }
  .dropup .dropdown-menu,
  .navbar-fixed-bottom .dropdown .dropdown-menu {
    top: auto;
    bottom: 100%;
    margin-bottom: 2px;
  }
  @media (min-width: 768px) {
    .navbar-right .dropdown-menu {
      right: 0;
      left: auto;
    }
    .navbar-right .dropdown-menu-left {
      right: auto;
      left: 0;
    }
  }
  .btn-group,
  .btn-group-vertical {
    position: relative;
    display: inline-block;
    vertical-align: middle;
  }
  .btn-group > .btn,
  .btn-group-vertical > .btn {
    position: relative;
    float: left;
  }
  .btn-group > .btn:hover,
  .btn-group-vertical > .btn:hover,
  .btn-group > .btn:focus,
  .btn-group-vertical > .btn:focus,
  .btn-group > .btn:active,
  .btn-group-vertical > .btn:active,
  .btn-group > .btn.active,
  .btn-group-vertical > .btn.active {
    z-index: 2;
  }
  .btn-group .btn + .btn,
  .btn-group .btn + .btn-group,
  .btn-group .btn-group + .btn,
  .btn-group .btn-group + .btn-group {
    margin-left: -1px;
  }
  .btn-toolbar {
    margin-left: -5px;
  }
  .btn-toolbar .btn-group,
  .btn-toolbar .input-group {
    float: left;
  }
  .btn-toolbar > .btn,
  .btn-toolbar > .btn-group,
  .btn-toolbar > .input-group {
    margin-left: 5px;
  }
  .btn-group > .btn:not(:first-child):not(:last-child):not(.dropdown-toggle) {
    border-radius: 0;
  }
  .btn-group > .btn:first-child {
    margin-left: 0;
  }
  .btn-group > .btn:first-child:not(:last-child):not(.dropdown-toggle) {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }
  .btn-group > .btn:last-child:not(:first-child),
  .btn-group > .dropdown-toggle:not(:first-child) {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
  .btn-group > .btn-group {
    float: left;
  }
  .btn-group > .btn-group:not(:first-child):not(:last-child) > .btn {
    border-radius: 0;
  }
  .btn-group > .btn-group:first-child > .btn:last-child,
  .btn-group > .btn-group:first-child > .dropdown-toggle {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }
  .btn-group > .btn-group:last-child > .btn:first-child {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
  .btn-group .dropdown-toggle:active,
  .btn-group.open .dropdown-toggle {
    outline: 0;
  }
  .btn-group > .btn + .dropdown-toggle {
    padding-right: 8px;
    padding-left: 8px;
  }
  .btn-group > .btn-lg + .dropdown-toggle {
    padding-right: 12px;
    padding-left: 12px;
  }
  .btn-group.open .dropdown-toggle {
    -webkit-box-shadow: inset 0 3px 5px rgba(0, 0, 0, .125);
            box-shadow: inset 0 3px 5px rgba(0, 0, 0, .125);
  }
  .btn-group.open .dropdown-toggle.btn-link {
    -webkit-box-shadow: none;
            box-shadow: none;
  }
  .btn .caret {
    margin-left: 0;
  }
  .btn-lg .caret {
    border-width: 5px 5px 0;
    border-bottom-width: 0;
  }
  .dropup .btn-lg .caret {
    border-width: 0 5px 5px;
  }
  .btn-group-vertical > .btn,
  .btn-group-vertical > .btn-group,
  .btn-group-vertical > .btn-group > .btn {
    display: block;
    float: none;
    width: 100%;
    max-width: 100%;
  }
  .btn-group-vertical > .btn-group > .btn {
    float: none;
  }
  .btn-group-vertical > .btn + .btn,
  .btn-group-vertical > .btn + .btn-group,
  .btn-group-vertical > .btn-group + .btn,
  .btn-group-vertical > .btn-group + .btn-group {
    margin-top: -1px;
    margin-left: 0;
  }
  .btn-group-vertical > .btn:not(:first-child):not(:last-child) {
    border-radius: 0;
  }
  .btn-group-vertical > .btn:first-child:not(:last-child) {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
  }
  .btn-group-vertical > .btn:last-child:not(:first-child) {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    border-bottom-left-radius: 4px;
  }
  .btn-group-vertical > .btn-group:not(:first-child):not(:last-child) > .btn {
    border-radius: 0;
  }
  .btn-group-vertical > .btn-group:first-child:not(:last-child) > .btn:last-child,
  .btn-group-vertical > .btn-group:first-child:not(:last-child) > .dropdown-toggle {
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
  }
  .btn-group-vertical > .btn-group:last-child:not(:first-child) > .btn:first-child {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }
  .btn-group-justified {
    display: table;
    width: 100%;
    table-layout: fixed;
    border-collapse: separate;
  }
  .btn-group-justified > .btn,
  .btn-group-justified > .btn-group {
    display: table-cell;
    float: none;
    width: 1%;
  }
  .btn-group-justified > .btn-group .btn {
    width: 100%;
  }
  .btn-group-justified > .btn-group .dropdown-menu {
    left: auto;
  }
  [data-toggle='buttons'] > .btn input[type='radio'],
  [data-toggle='buttons'] > .btn-group > .btn input[type='radio'],
  [data-toggle='buttons'] > .btn input[type='checkbox'],
  [data-toggle='buttons'] > .btn-group > .btn input[type='checkbox'] {
    position: absolute;
    clip: rect(0, 0, 0, 0);
    pointer-events: none;
  }
  .input-group {
    position: relative;
    display: table;
    border-collapse: separate;
  }
  .input-group[class*='col-'] {
    float: none;
    padding-right: 0;
    padding-left: 0;
  }
  .input-group .form-control {
    position: relative;
    z-index: 2;
    float: left;
    width: 100%;
    margin-bottom: 0;
  }
  .input-group-lg > .form-control,
  .input-group-lg > .input-group-addon,
  .input-group-lg > .input-group-btn > .btn {
    height: 46px;
    padding: 10px 16px;
    font-size: 18px;
    line-height: 1.33;
    border-radius: 6px;
  }
  select.input-group-lg > .form-control,
  select.input-group-lg > .input-group-addon,
  select.input-group-lg > .input-group-btn > .btn {
    height: 46px;
    line-height: 46px;
  }
  textarea.input-group-lg > .form-control,
  textarea.input-group-lg > .input-group-addon,
  textarea.input-group-lg > .input-group-btn > .btn,
  select[multiple].input-group-lg > .form-control,
  select[multiple].input-group-lg > .input-group-addon,
  select[multiple].input-group-lg > .input-group-btn > .btn {
    height: auto;
  }
  .input-group-sm > .form-control,
  .input-group-sm > .input-group-addon,
  .input-group-sm > .input-group-btn > .btn {
    height: 30px;
    padding: 5px 10px;
    font-size: 12px;
    line-height: 1.5;
    border-radius: 3px;
  }
  select.input-group-sm > .form-control,
  select.input-group-sm > .input-group-addon,
  select.input-group-sm > .input-group-btn > .btn {
    height: 30px;
    line-height: 30px;
  }
  textarea.input-group-sm > .form-control,
  textarea.input-group-sm > .input-group-addon,
  textarea.input-group-sm > .input-group-btn > .btn,
  select[multiple].input-group-sm > .form-control,
  select[multiple].input-group-sm > .input-group-addon,
  select[multiple].input-group-sm > .input-group-btn > .btn {
    height: auto;
  }
  .input-group-addon,
  .input-group-btn,
  .input-group .form-control {
    display: table-cell;
  }
  .input-group-addon:not(:first-child):not(:last-child),
  .input-group-btn:not(:first-child):not(:last-child),
  .input-group .form-control:not(:first-child):not(:last-child) {
    border-radius: 0;
  }
  .input-group-addon,
  .input-group-btn {
    width: 1%;
    white-space: nowrap;
    vertical-align: middle;
  }
  .input-group-addon {
    padding: 4px 10px;
    font-size: 14px;
    font-weight: normal;
    line-height: 1;
    color: #555;
    text-align: center;
    background-color: #f0f4f7;
    border: 1px solid #d1d8dd;
    border-radius: 4px;
  }
  .input-group-addon.input-sm {
    padding: 5px 10px;
    font-size: 12px;
    border-radius: 3px;
  }
  .input-group-addon.input-lg {
    padding: 10px 16px;
    font-size: 18px;
    border-radius: 6px;
  }
  .input-group-addon input[type='radio'],
  .input-group-addon input[type='checkbox'] {
    margin-top: 0;
  }
  .input-group .form-control:first-child,
  .input-group-addon:first-child,
  .input-group-btn:first-child > .btn,
  .input-group-btn:first-child > .btn-group > .btn,
  .input-group-btn:first-child > .dropdown-toggle,
  .input-group-btn:last-child > .btn:not(:last-child):not(.dropdown-toggle),
  .input-group-btn:last-child > .btn-group:not(:last-child) > .btn {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }
  .input-group-addon:first-child {
    border-right: 0;
  }
  .input-group .form-control:last-child,
  .input-group-addon:last-child,
  .input-group-btn:last-child > .btn,
  .input-group-btn:last-child > .btn-group > .btn,
  .input-group-btn:last-child > .dropdown-toggle,
  .input-group-btn:first-child > .btn:not(:first-child),
  .input-group-btn:first-child > .btn-group:not(:first-child) > .btn {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
  .input-group-addon:last-child {
    border-left: 0;
  }
  .input-group-btn {
    position: relative;
    font-size: 0;
    white-space: nowrap;
  }
  .input-group-btn > .btn {
    position: relative;
  }
  .input-group-btn > .btn + .btn {
    margin-left: -1px;
  }
  .input-group-btn > .btn:hover,
  .input-group-btn > .btn:focus,
  .input-group-btn > .btn:active {
    z-index: 2;
  }
  .input-group-btn:first-child > .btn,
  .input-group-btn:first-child > .btn-group {
    margin-right: -1px;
  }
  .input-group-btn:last-child > .btn,
  .input-group-btn:last-child > .btn-group {
    margin-left: -1px;
  }
  .nav {
    padding-left: 0;
    margin-bottom: 0;
    list-style: none;
  }
  .nav > li {
    position: relative;
    display: block;
  }
  .nav > li > a {
    position: relative;
    display: block;
    padding: 10px 15px;
  }
  .nav > li > a:hover,
  .nav > li > a:focus {
    text-decoration: none;
    background-color: #f7fafc;
  }
  .nav > li.disabled > a {
    color: #777;
  }
  .nav > li.disabled > a:hover,
  .nav > li.disabled > a:focus {
    color: #777;
    text-decoration: none;
    cursor: not-allowed;
    background-color: transparent;
  }
  .nav .open > a,
  .nav .open > a:hover,
  .nav .open > a:focus {
    background-color: #f7fafc;
    border-color: #36414c;
  }
  .nav .nav-divider {
    height: 1px;
    margin: 9px 0;
    overflow: hidden;
    background-color: #e5e5e5;
  }
  .nav > li > a > img {
    max-width: none;
  }
  .nav-tabs {
    border-bottom: 1px solid #ddd;
  }
  .nav-tabs > li {
    float: left;
    margin-bottom: -1px;
  }
  .nav-tabs > li > a {
    margin-right: 2px;
    line-height: 1.42857143;
    border: 1px solid transparent;
    border-radius: 4px 4px 0 0;
  }
  .nav-tabs > li > a:hover {
    border-color: #eee #eee #ddd;
  }
  .nav-tabs > li.active > a,
  .nav-tabs > li.active > a:hover,
  .nav-tabs > li.active > a:focus {
    color: #555;
    cursor: default;
    background-color: #fff;
    border: 1px solid #ddd;
    border-bottom-color: transparent;
  }
  .nav-tabs.nav-justified {
    width: 100%;
    border-bottom: 0;
  }
  .nav-tabs.nav-justified > li {
    float: none;
  }
  .nav-tabs.nav-justified > li > a {
    margin-bottom: 5px;
    text-align: center;
  }
  .nav-tabs.nav-justified > .dropdown .dropdown-menu {
    top: auto;
    left: auto;
  }
  @media (min-width: 768px) {
    .nav-tabs.nav-justified > li {
      display: table-cell;
      width: 1%;
    }
    .nav-tabs.nav-justified > li > a {
      margin-bottom: 0;
    }
  }
  .nav-tabs.nav-justified > li > a {
    margin-right: 0;
    border-radius: 4px;
  }
  .nav-tabs.nav-justified > .active > a,
  .nav-tabs.nav-justified > .active > a:hover,
  .nav-tabs.nav-justified > .active > a:focus {
    border: 1px solid #ddd;
  }
  @media (min-width: 768px) {
    .nav-tabs.nav-justified > li > a {
      border-bottom: 1px solid #ddd;
      border-radius: 4px 4px 0 0;
    }
    .nav-tabs.nav-justified > .active > a,
    .nav-tabs.nav-justified > .active > a:hover,
    .nav-tabs.nav-justified > .active > a:focus {
      border-bottom-color: #fff;
    }
  }
  .nav-pills > li {
    float: left;
  }
  .nav-pills > li > a {
    border-radius: 4px;
  }
  .nav-pills > li + li {
    margin-left: 2px;
  }
  .nav-pills > li.active > a,
  .nav-pills > li.active > a:hover,
  .nav-pills > li.active > a:focus {
    color: inherit;
    background-color: #f7fafc;
  }
  .nav-stacked > li {
    float: none;
  }
  .nav-stacked > li + li {
    margin-top: 2px;
    margin-left: 0;
  }
  .nav-justified {
    width: 100%;
  }
  .nav-justified > li {
    float: none;
  }
  .nav-justified > li > a {
    margin-bottom: 5px;
    text-align: center;
  }
  .nav-justified > .dropdown .dropdown-menu {
    top: auto;
    left: auto;
  }
  @media (min-width: 768px) {
    .nav-justified > li {
      display: table-cell;
      width: 1%;
    }
    .nav-justified > li > a {
      margin-bottom: 0;
    }
  }
  .nav-tabs-justified {
    border-bottom: 0;
  }
  .nav-tabs-justified > li > a {
    margin-right: 0;
    border-radius: 4px;
  }
  .nav-tabs-justified > .active > a,
  .nav-tabs-justified > .active > a:hover,
  .nav-tabs-justified > .active > a:focus {
    border: 1px solid #ddd;
  }
  @media (min-width: 768px) {
    .nav-tabs-justified > li > a {
      border-bottom: 1px solid #ddd;
      border-radius: 4px 4px 0 0;
    }
    .nav-tabs-justified > .active > a,
    .nav-tabs-justified > .active > a:hover,
    .nav-tabs-justified > .active > a:focus {
      border-bottom-color: #fff;
    }
  }
  .tab-content > .tab-pane {
    display: none;
    visibility: hidden;
  }
  .tab-content > .active {
    display: block;
    visibility: visible;
  }
  .nav-tabs .dropdown-menu {
    margin-top: -1px;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }
  .navbar {
    position: relative;
    min-height: 40px;
    margin-bottom: 20px;
    border: 1px solid transparent;
  }
  @media (min-width: 768px) {
    .navbar {
      border-radius: 4px;
    }
  }
  @media (min-width: 768px) {
    .navbar-header {
      float: left;
    }
  }
  .navbar-collapse {
    padding-right: 15px;
    padding-left: 15px;
    overflow-x: visible;
    -webkit-overflow-scrolling: touch;
    border-top: 1px solid transparent;
    -webkit-box-shadow: inset 0 1px 0 rgba(255, 255, 255, .1);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, .1);
  }
  .navbar-collapse.in {
    overflow-y: auto;
  }
  @media (min-width: 768px) {
    .navbar-collapse {
      width: auto;
      border-top: 0;
      -webkit-box-shadow: none;
              box-shadow: none;
    }
    .navbar-collapse.collapse {
      display: block !important;
      height: auto !important;
      padding-bottom: 0;
      overflow: visible !important;
      visibility: visible !important;
    }
    .navbar-collapse.in {
      overflow-y: visible;
    }
    .navbar-fixed-top .navbar-collapse,
    .navbar-static-top .navbar-collapse,
    .navbar-fixed-bottom .navbar-collapse {
      padding-right: 0;
      padding-left: 0;
    }
  }
  .navbar-fixed-top .navbar-collapse,
  .navbar-fixed-bottom .navbar-collapse {
    max-height: 340px;
  }
  @media (max-device-width: 480px) and (orientation: landscape) {
    .navbar-fixed-top .navbar-collapse,
    .navbar-fixed-bottom .navbar-collapse {
      max-height: 200px;
    }
  }
  .container > .navbar-header,
  .container-fluid > .navbar-header,
  .container > .navbar-collapse,
  .container-fluid > .navbar-collapse {
    margin-right: -15px;
    margin-left: -15px;
  }
  @media (min-width: 768px) {
    .container > .navbar-header,
    .container-fluid > .navbar-header,
    .container > .navbar-collapse,
    .container-fluid > .navbar-collapse {
      margin-right: 0;
      margin-left: 0;
    }
  }
  .navbar-static-top {
    z-index: 1000;
    border-width: 0 0 1px;
  }
  @media (min-width: 768px) {
    .navbar-static-top {
      border-radius: 0;
    }
  }
  .navbar-fixed-top,
  .navbar-fixed-bottom {
    position: fixed;
    right: 0;
    left: 0;
    z-index: 1030;
  }
  @media (min-width: 768px) {
    .navbar-fixed-top,
    .navbar-fixed-bottom {
      border-radius: 0;
    }
  }
  .navbar-fixed-top {
    top: 0;
    border-width: 0 0 1px;
  }
  .navbar-fixed-bottom {
    bottom: 0;
    margin-bottom: 0;
    border-width: 1px 0 0;
  }
  .navbar-brand {
    float: left;
    height: 40px;
    padding: 10px 15px;
    font-size: 18px;
    line-height: 20px;
  }
  .navbar-brand:hover,
  .navbar-brand:focus {
    text-decoration: none;
  }
  .navbar-brand > img {
    display: block;
  }
  @media (min-width: 768px) {
    .navbar > .container .navbar-brand,
    .navbar > .container-fluid .navbar-brand {
      margin-left: -15px;
    }
  }
  .navbar-toggle {
    position: relative;
    float: right;
    padding: 9px 10px;
    margin-top: 3px;
    margin-right: 15px;
    margin-bottom: 3px;
    background-color: transparent;
    background-image: none;
    border: 1px solid transparent;
    border-radius: 4px;
  }
  .navbar-toggle:focus {
    outline: 0;
  }
  .navbar-toggle .icon-bar {
    display: block;
    width: 22px;
    height: 2px;
    border-radius: 1px;
  }
  .navbar-toggle .icon-bar + .icon-bar {
    margin-top: 4px;
  }
  @media (min-width: 768px) {
    .navbar-toggle {
      display: none;
    }
  }
  .navbar-nav {
    margin: 5px -15px;
  }
  .navbar-nav > li > a {
    padding-top: 10px;
    padding-bottom: 10px;
    line-height: 20px;
  }
  @media (max-width: 767px) {
    .navbar-nav .open .dropdown-menu {
      position: static;
      float: none;
      width: auto;
      margin-top: 0;
      background-color: transparent;
      border: 0;
      -webkit-box-shadow: none;
              box-shadow: none;
    }
    .navbar-nav .open .dropdown-menu > li > a,
    .navbar-nav .open .dropdown-menu .dropdown-header {
      padding: 5px 15px 5px 25px;
    }
    .navbar-nav .open .dropdown-menu > li > a {
      line-height: 20px;
    }
    .navbar-nav .open .dropdown-menu > li > a:hover,
    .navbar-nav .open .dropdown-menu > li > a:focus {
      background-image: none;
    }
  }
  @media (min-width: 768px) {
    .navbar-nav {
      float: left;
      margin: 0;
    }
    .navbar-nav > li {
      float: left;
    }
    .navbar-nav > li > a {
      padding-top: 10px;
      padding-bottom: 10px;
    }
  }
  .navbar-form {
    padding: 10px 15px;
    margin-top: 5px;
    margin-right: -15px;
    margin-bottom: 5px;
    margin-left: -15px;
    border-top: 1px solid transparent;
    border-bottom: 1px solid transparent;
    -webkit-box-shadow: inset 0 1px 0 rgba(255, 255, 255, .1), 0 1px 0 rgba(255, 255, 255, .1);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, .1), 0 1px 0 rgba(255, 255, 255, .1);
  }
  @media (min-width: 768px) {
    .navbar-form .form-group {
      display: inline-block;
      margin-bottom: 0;
      vertical-align: middle;
    }
    .navbar-form .form-control {
      display: inline-block;
      width: auto;
      vertical-align: middle;
    }
    .navbar-form .form-control-static {
      display: inline-block;
    }
    .navbar-form .input-group {
      display: inline-table;
      vertical-align: middle;
    }
    .navbar-form .input-group .input-group-addon,
    .navbar-form .input-group .input-group-btn,
    .navbar-form .input-group .form-control {
      width: auto;
    }
    .navbar-form .input-group > .form-control {
      width: 100%;
    }
    .navbar-form .control-label {
      margin-bottom: 0;
      vertical-align: middle;
    }
    .navbar-form .radio,
    .navbar-form .checkbox {
      display: inline-block;
      margin-top: 0;
      margin-bottom: 0;
      vertical-align: middle;
    }
    .navbar-form .radio label,
    .navbar-form .checkbox label {
      padding-left: 0;
    }
    .navbar-form .radio input[type='radio'],
    .navbar-form .checkbox input[type='checkbox'] {
      position: relative;
      margin-left: 0;
    }
    .navbar-form .has-feedback .form-control-feedback {
      top: 0;
    }
  }
  @media (max-width: 767px) {
    .navbar-form .form-group {
      margin-bottom: 5px;
    }
    .navbar-form .form-group:last-child {
      margin-bottom: 0;
    }
  }
  @media (min-width: 768px) {
    .navbar-form {
      width: auto;
      padding-top: 0;
      padding-bottom: 0;
      margin-right: 0;
      margin-left: 0;
      border: 0;
      -webkit-box-shadow: none;
              box-shadow: none;
    }
  }
  .navbar-nav > li > .dropdown-menu {
    margin-top: 0;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }
  .navbar-fixed-bottom .navbar-nav > li > .dropdown-menu {
    margin-bottom: 0;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
  }
  .navbar-btn {
    margin-top: 5px;
    margin-bottom: 5px;
  }
  .navbar-btn.btn-sm {
    margin-top: 5px;
    margin-bottom: 5px;
  }
  .navbar-btn.btn-xs {
    margin-top: 9px;
    margin-bottom: 9px;
  }
  .navbar-text {
    margin-top: 10px;
    margin-bottom: 10px;
  }
  @media (min-width: 768px) {
    .navbar-text {
      float: left;
      margin-right: 15px;
      margin-left: 15px;
    }
  }
  @media (min-width: 768px) {
    .navbar-left {
      float: left !important;
    }
    .navbar-right {
      float: right !important;
      margin-right: -15px;
    }
    .navbar-right ~ .navbar-right {
      margin-right: 0;
    }
  }
  .navbar-default {
    background-color: #f5f7fa;
    border-color: #ebeff2;
  }
  .navbar-default .navbar-brand {
    color: #6c7680;
  }
  .navbar-default .navbar-brand:hover,
  .navbar-default .navbar-brand:focus {
    color: #36414c;
    background-color: transparent;
  }
  .navbar-default .navbar-text {
    color: #6c7680;
  }
  .navbar-default .navbar-nav > li > a {
    color: #6c7680;
  }
  .navbar-default .navbar-nav > li > a:hover,
  .navbar-default .navbar-nav > li > a:focus {
    color: #36414c;
    background-color: transparent;
  }
  .navbar-default .navbar-nav > .active > a,
  .navbar-default .navbar-nav > .active > a:hover,
  .navbar-default .navbar-nav > .active > a:focus {
    color: #555;
    background-color: #dfe5ef;
  }
  .navbar-default .navbar-nav > .disabled > a,
  .navbar-default .navbar-nav > .disabled > a:hover,
  .navbar-default .navbar-nav > .disabled > a:focus {
    color: #ccc;
    background-color: transparent;
  }
  .navbar-default .navbar-toggle {
    border-color: #ddd;
  }
  .navbar-default .navbar-toggle:hover,
  .navbar-default .navbar-toggle:focus {
    background-color: #ddd;
  }
  .navbar-default .navbar-toggle .icon-bar {
    background-color: #888;
  }
  .navbar-default .navbar-collapse,
  .navbar-default .navbar-form {
    border-color: #ebeff2;
  }
  .navbar-default .navbar-nav > .open > a,
  .navbar-default .navbar-nav > .open > a:hover,
  .navbar-default .navbar-nav > .open > a:focus {
    color: #555;
    background-color: #dfe5ef;
  }
  @media (max-width: 767px) {
    .navbar-default .navbar-nav .open .dropdown-menu > li > a {
      color: #6c7680;
    }
    .navbar-default .navbar-nav .open .dropdown-menu > li > a:hover,
    .navbar-default .navbar-nav .open .dropdown-menu > li > a:focus {
      color: #36414c;
      background-color: transparent;
    }
    .navbar-default .navbar-nav .open .dropdown-menu > .active > a,
    .navbar-default .navbar-nav .open .dropdown-menu > .active > a:hover,
    .navbar-default .navbar-nav .open .dropdown-menu > .active > a:focus {
      color: #555;
      background-color: #dfe5ef;
    }
    .navbar-default .navbar-nav .open .dropdown-menu > .disabled > a,
    .navbar-default .navbar-nav .open .dropdown-menu > .disabled > a:hover,
    .navbar-default .navbar-nav .open .dropdown-menu > .disabled > a:focus {
      color: #ccc;
      background-color: transparent;
    }
  }
  .navbar-default .navbar-link {
    color: #6c7680;
  }
  .navbar-default .navbar-link:hover {
    color: #36414c;
  }
  .navbar-default .btn-link {
    color: #6c7680;
  }
  .navbar-default .btn-link:hover,
  .navbar-default .btn-link:focus {
    color: #36414c;
  }
  .navbar-default .btn-link[disabled]:hover,
  fieldset[disabled] .navbar-default .btn-link:hover,
  .navbar-default .btn-link[disabled]:focus,
  fieldset[disabled] .navbar-default .btn-link:focus {
    color: #ccc;
  }
  .navbar-inverse {
    background-color: #35414b;
    border-color: #2a343c;
  }
  .navbar-inverse .navbar-brand {
    color: #9d9d9d;
  }
  .navbar-inverse .navbar-brand:hover,
  .navbar-inverse .navbar-brand:focus {
    color: #fff;
    background-color: transparent;
  }
  .navbar-inverse .navbar-text {
    color: #b8c2cb;
  }
  .navbar-inverse .navbar-nav > li > a {
    color: #9d9d9d;
  }
  .navbar-inverse .navbar-nav > li > a:hover,
  .navbar-inverse .navbar-nav > li > a:focus {
    color: #fff;
    background-color: transparent;
  }
  .navbar-inverse .navbar-nav > .active > a,
  .navbar-inverse .navbar-nav > .active > a:hover,
  .navbar-inverse .navbar-nav > .active > a:focus {
    color: #fff;
    background-color: #20272d;
  }
  .navbar-inverse .navbar-nav > .disabled > a,
  .navbar-inverse .navbar-nav > .disabled > a:hover,
  .navbar-inverse .navbar-nav > .disabled > a:focus {
    color: #475765;
    background-color: transparent;
  }
  .navbar-inverse .navbar-toggle {
    border-color: #475765;
  }
  .navbar-inverse .navbar-toggle:hover,
  .navbar-inverse .navbar-toggle:focus {
    background-color: #475765;
  }
  .navbar-inverse .navbar-toggle .icon-bar {
    background-color: #fff;
  }
  .navbar-inverse .navbar-collapse,
  .navbar-inverse .navbar-form {
    border-color: #262f36;
  }
  .navbar-inverse .navbar-nav > .open > a,
  .navbar-inverse .navbar-nav > .open > a:hover,
  .navbar-inverse .navbar-nav > .open > a:focus {
    color: #fff;
    background-color: #20272d;
  }
  @media (max-width: 767px) {
    .navbar-inverse .navbar-nav .open .dropdown-menu > .dropdown-header {
      border-color: #2a343c;
    }
    .navbar-inverse .navbar-nav .open .dropdown-menu .divider {
      background-color: #2a343c;
    }
    .navbar-inverse .navbar-nav .open .dropdown-menu > li > a {
      color: #9d9d9d;
    }
    .navbar-inverse .navbar-nav .open .dropdown-menu > li > a:hover,
    .navbar-inverse .navbar-nav .open .dropdown-menu > li > a:focus {
      color: #fff;
      background-color: transparent;
    }
    .navbar-inverse .navbar-nav .open .dropdown-menu > .active > a,
    .navbar-inverse .navbar-nav .open .dropdown-menu > .active > a:hover,
    .navbar-inverse .navbar-nav .open .dropdown-menu > .active > a:focus {
      color: #fff;
      background-color: #20272d;
    }
    .navbar-inverse .navbar-nav .open .dropdown-menu > .disabled > a,
    .navbar-inverse .navbar-nav .open .dropdown-menu > .disabled > a:hover,
    .navbar-inverse .navbar-nav .open .dropdown-menu > .disabled > a:focus {
      color: #475765;
      background-color: transparent;
    }
  }
  .navbar-inverse .navbar-link {
    color: #9d9d9d;
  }
  .navbar-inverse .navbar-link:hover {
    color: #fff;
  }
  .navbar-inverse .btn-link {
    color: #9d9d9d;
  }
  .navbar-inverse .btn-link:hover,
  .navbar-inverse .btn-link:focus {
    color: #fff;
  }
  .navbar-inverse .btn-link[disabled]:hover,
  fieldset[disabled] .navbar-inverse .btn-link:hover,
  .navbar-inverse .btn-link[disabled]:focus,
  fieldset[disabled] .navbar-inverse .btn-link:focus {
    color: #475765;
  }
  .breadcrumb {
    padding: 8px 15px;
    margin-bottom: 20px;
    list-style: none;
    background-color: #f5f5f5;
    border-radius: 4px;
  }
  .breadcrumb > li {
    display: inline-block;
  }
  .breadcrumb > li + li:before {
    padding: 0 5px;
    color: #ccc;
    content: 'NONE';
  }
  .breadcrumb > .active {
    color: #777;
  }
  .pagination {
    display: inline-block;
    padding-left: 0;
    margin: 20px 0;
    border-radius: 4px;
  }
  .pagination > li {
    display: inline;
  }
  .pagination > li > a,
  .pagination > li > span {
    position: relative;
    float: left;
    padding: 4px 10px;
    margin-left: -1px;
    line-height: 1.42857143;
    color: #36414c;
    text-decoration: none;
    background-color: #fff;
    border: 1px solid #ddd;
  }
  .pagination > li:first-child > a,
  .pagination > li:first-child > span {
    margin-left: 0;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
  }
  .pagination > li:last-child > a,
  .pagination > li:last-child > span {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
  }
  .pagination > li > a:hover,
  .pagination > li > span:hover,
  .pagination > li > a:focus,
  .pagination > li > span:focus {
    color: #161b1f;
    background-color: #eee;
    border-color: #ddd;
  }
  .pagination > .active > a,
  .pagination > .active > span,
  .pagination > .active > a:hover,
  .pagination > .active > span:hover,
  .pagination > .active > a:focus,
  .pagination > .active > span:focus {
    z-index: 2;
    color: #fff;
    cursor: default;
    background-color: #5e64ff;
    border-color: #5e64ff;
  }
  .pagination > .disabled > span,
  .pagination > .disabled > span:hover,
  .pagination > .disabled > span:focus,
  .pagination > .disabled > a,
  .pagination > .disabled > a:hover,
  .pagination > .disabled > a:focus {
    color: #777;
    cursor: not-allowed;
    background-color: #fff;
    border-color: #ddd;
  }
  .pagination-lg > li > a,
  .pagination-lg > li > span {
    padding: 10px 16px;
    font-size: 18px;
  }
  .pagination-lg > li:first-child > a,
  .pagination-lg > li:first-child > span {
    border-top-left-radius: 6px;
    border-bottom-left-radius: 6px;
  }
  .pagination-lg > li:last-child > a,
  .pagination-lg > li:last-child > span {
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
  }
  .pagination-sm > li > a,
  .pagination-sm > li > span {
    padding: 5px 10px;
    font-size: 12px;
  }
  .pagination-sm > li:first-child > a,
  .pagination-sm > li:first-child > span {
    border-top-left-radius: 3px;
    border-bottom-left-radius: 3px;
  }
  .pagination-sm > li:last-child > a,
  .pagination-sm > li:last-child > span {
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
  }
  .pager {
    padding-left: 0;
    margin: 20px 0;
    text-align: center;
    list-style: none;
  }
  .pager li {
    display: inline;
  }
  .pager li > a,
  .pager li > span {
    display: inline-block;
    padding: 5px 14px;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 15px;
  }
  .pager li > a:hover,
  .pager li > a:focus {
    text-decoration: none;
    background-color: #eee;
  }
  .pager .next > a,
  .pager .next > span {
    float: right;
  }
  .pager .previous > a,
  .pager .previous > span {
    float: left;
  }
  .pager .disabled > a,
  .pager .disabled > a:hover,
  .pager .disabled > a:focus,
  .pager .disabled > span {
    color: #777;
    cursor: not-allowed;
    background-color: #fff;
  }
  .label {
    display: inline;
    padding: .2em .6em .3em;
    font-size: 75%;
    font-weight: bold;
    line-height: 1;
    color: inherit;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: .25em;
  }
  a.label:hover,
  a.label:focus {
    color: #fff;
    text-decoration: none;
    cursor: pointer;
  }
  .label:empty {
    display: none;
  }
  .btn .label {
    position: relative;
    top: -1px;
  }
  .label-default {
    background-color: #f0f4f7;
  }
  .label-default[href]:hover,
  .label-default[href]:focus {
    background-color: #cfdce5;
  }
  .label-primary {
    background-color: #d9f6ff;
  }
  .label-primary[href]:hover,
  .label-primary[href]:focus {
    background-color: #a6eaff;
  }
  .label-success {
    background-color: #e4ffc1;
  }
  .label-success[href]:hover,
  .label-success[href]:focus {
    background-color: #ceff8e;
  }
  .label-info {
    background-color: #e8ddff;
  }
  .label-info[href]:hover,
  .label-info[href]:focus {
    background-color: #c6aaff;
  }
  .label-warning {
    background-color: #ffe6bf;
  }
  .label-warning[href]:hover,
  .label-warning[href]:focus {
    background-color: #ffd28c;
  }
  .label-danger {
    background-color: #ffdcdc;
  }
  .label-danger[href]:hover,
  .label-danger[href]:focus {
    background-color: #ffa9a9;
  }
  .badge {
    display: inline-block;
    min-width: 10px;
    padding: 3px 7px;
    font-size: 12px;
    font-weight: bold;
    line-height: 1;
    color: #36414c;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    background-color: #f0f4f7;
    border-radius: 10px;
  }
  .badge:empty {
    display: none;
  }
  .btn .badge {
    position: relative;
    top: -1px;
  }
  .btn-xs .badge {
    top: 0;
    padding: 1px 5px;
  }
  a.badge:hover,
  a.badge:focus {
    color: #fff;
    text-decoration: none;
    cursor: pointer;
  }
  .list-group-item.active > .badge,
  .nav-pills > .active > a > .badge {
    color: #36414c;
    background-color: #fff;
  }
  .list-group-item > .badge {
    float: right;
  }
  .list-group-item > .badge + .badge {
    margin-right: 5px;
  }
  .nav-pills > li > a > .badge {
    margin-left: 3px;
  }
  .jumbotron {
    padding: 30px 15px;
    margin-bottom: 30px;
    color: inherit;
    background-color: #eee;
  }
  .jumbotron h1,
  .jumbotron .h1 {
    color: inherit;
  }
  .jumbotron p {
    margin-bottom: 15px;
    font-size: 21px;
    font-weight: 200;
  }
  .jumbotron > hr {
    border-top-color: #d5d5d5;
  }
  .container .jumbotron,
  .container-fluid .jumbotron {
    border-radius: 6px;
  }
  .jumbotron .container {
    max-width: 100%;
  }
  @media screen and (min-width: 768px) {
    .jumbotron {
      padding: 48px 0;
    }
    .container .jumbotron,
    .container-fluid .jumbotron {
      padding-right: 60px;
      padding-left: 60px;
    }
    .jumbotron h1,
    .jumbotron .h1 {
      font-size: 63px;
    }
  }
  .thumbnail {
    display: block;
    padding: 4px;
    margin-bottom: 20px;
    line-height: 1.42857143;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    -webkit-transition: border .2s ease-in-out;
         -o-transition: border .2s ease-in-out;
            transition: border .2s ease-in-out;
  }
  .thumbnail > img,
  .thumbnail a > img {
    margin-right: auto;
    margin-left: auto;
  }
  a.thumbnail:hover,
  a.thumbnail:focus,
  a.thumbnail.active {
    border-color: #36414c;
  }
  .thumbnail .caption {
    padding: 9px;
    color: #36414c;
  }
  .alert {
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid transparent;
    border-radius: 4px;
  }
  .alert h4 {
    margin-top: 0;
    color: inherit;
  }
  .alert .alert-link {
    font-weight: bold;
  }
  .alert > p,
  .alert > ul {
    margin-bottom: 0;
  }
  .alert > p + p {
    margin-top: 5px;
  }
  .alert-dismissable,
  .alert-dismissible {
    padding-right: 30px;
  }
  .alert-dismissable .close,
  .alert-dismissible .close {
    position: relative;
    top: -2px;
    right: -21px;
    color: inherit;
  }
  .alert-success {
    color: #98d85b;
    background-color: rgba(255, 255, 255, .9);
    border-color: #98d85b;
  }
  .alert-success hr {
    border-top-color: #8bd346;
  }
  .alert-success .alert-link {
    color: #7ece32;
  }
  .alert-info {
    color: #935eff;
    background-color: rgba(255, 255, 255, .9);
    border-color: #935eff;
  }
  .alert-info hr {
    border-top-color: #8244ff;
  }
  .alert-info .alert-link {
    color: #712bff;
  }
  .alert-warning {
    color: #ffa00a;
    background-color: rgba(255, 255, 255, .9);
    border-color: #ffa00a;
  }
  .alert-warning hr {
    border-top-color: #f09300;
  }
  .alert-warning .alert-link {
    color: #d68300;
  }
  .alert-danger {
    color: #ff5858;
    background-color: rgba(255, 255, 255, .9);
    border-color: #ff5858;
  }
  .alert-danger hr {
    border-top-color: #ff3f3f;
  }
  .alert-danger .alert-link {
    color: #ff2525;
  }
  @-webkit-keyframes progress-bar-stripes {
    from {
      background-position: 40px 0;
    }
    to {
      background-position: 0 0;
    }
  }
  @-o-keyframes progress-bar-stripes {
    from {
      background-position: 40px 0;
    }
    to {
      background-position: 0 0;
    }
  }
  @keyframes progress-bar-stripes {
    from {
      background-position: 40px 0;
    }
    to {
      background-position: 0 0;
    }
  }
  .progress {
    height: 20px;
    margin-bottom: 20px;
    overflow: hidden;
    background-color: #f5f5f5;
    border-radius: 4px;
    -webkit-box-shadow: inset 0 1px 2px rgba(0, 0, 0, .1);
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, .1);
  }
  .progress-bar {
    float: left;
    width: 0;
    height: 100%;
    font-size: 12px;
    line-height: 20px;
    color: #fff;
    text-align: center;
    background-color: #36414c;
    -webkit-box-shadow: inset 0 -1px 0 rgba(0, 0, 0, .15);
            box-shadow: inset 0 -1px 0 rgba(0, 0, 0, .15);
    -webkit-transition: width .6s ease;
         -o-transition: width .6s ease;
            transition: width .6s ease;
  }
  .progress-striped .progress-bar,
  .progress-bar-striped {
    background-image: -webkit-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:      -o-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:         linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    -webkit-background-size: 40px 40px;
            background-size: 40px 40px;
  }
  .progress.active .progress-bar,
  .progress-bar.active {
    -webkit-animation: progress-bar-stripes 2s linear infinite;
         -o-animation: progress-bar-stripes 2s linear infinite;
            animation: progress-bar-stripes 2s linear infinite;
  }
  .progress-bar-success {
    background-color: #98d85b;
  }
  .progress-striped .progress-bar-success {
    background-image: -webkit-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:      -o-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:         linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
  }
  .progress-bar-info {
    background-color: #935eff;
  }
  .progress-striped .progress-bar-info {
    background-image: -webkit-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:      -o-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:         linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
  }
  .progress-bar-warning {
    background-color: #ffa00a;
  }
  .progress-striped .progress-bar-warning {
    background-image: -webkit-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:      -o-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:         linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
  }
  .progress-bar-danger {
    background-color: #ff5858;
  }
  .progress-striped .progress-bar-danger {
    background-image: -webkit-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:      -o-linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
    background-image:         linear-gradient(45deg, rgba(255, 255, 255, .15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, .15) 50%, rgba(255, 255, 255, .15) 75%, transparent 75%, transparent);
  }
  .media {
    margin-top: 15px;
  }
  .media:first-child {
    margin-top: 0;
  }
  .media,
  .media-body {
    overflow: hidden;
    zoom: 1;
  }
  .media-body {
    width: 10000px;
  }
  .media-object {
    display: block;
  }
  .media-right,
  .media > .pull-right {
    padding-left: 10px;
  }
  .media-left,
  .media > .pull-left {
    padding-right: 10px;
  }
  .media-left,
  .media-right,
  .media-body {
    display: table-cell;
    vertical-align: top;
  }
  .media-middle {
    vertical-align: middle;
  }
  .media-bottom {
    vertical-align: bottom;
  }
  .media-heading {
    margin-top: 0;
    margin-bottom: 5px;
  }
  .media-list {
    padding-left: 0;
    list-style: none;
  }
  .list-group {
    padding-left: 0;
    margin-bottom: 20px;
  }
  .list-group-item {
    position: relative;
    display: block;
    padding: 10px 15px;
    margin-bottom: -1px;
    background-color: #fff;
    border: 1px solid #ddd;
  }
  .list-group-item:first-child {
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
  }
  .list-group-item:last-child {
    margin-bottom: 0;
    border-bottom-right-radius: 4px;
    border-bottom-left-radius: 4px;
  }
  a.list-group-item {
    color: #555;
  }
  a.list-group-item .list-group-item-heading {
    color: #333;
  }
  a.list-group-item:hover,
  a.list-group-item:focus {
    color: #555;
    text-decoration: none;
    background-color: #f5f5f5;
  }
  .list-group-item.disabled,
  .list-group-item.disabled:hover,
  .list-group-item.disabled:focus {
    color: #777;
    cursor: not-allowed;
    background-color: #eee;
  }
  .list-group-item.disabled .list-group-item-heading,
  .list-group-item.disabled:hover .list-group-item-heading,
  .list-group-item.disabled:focus .list-group-item-heading {
    color: inherit;
  }
  .list-group-item.disabled .list-group-item-text,
  .list-group-item.disabled:hover .list-group-item-text,
  .list-group-item.disabled:focus .list-group-item-text {
    color: #777;
  }
  .list-group-item.active,
  .list-group-item.active:hover,
  .list-group-item.active:focus {
    z-index: 2;
    color: inherit;
    background-color: #f0f4f7;
    border-color: #f0f4f7;
  }
  .list-group-item.active .list-group-item-heading,
  .list-group-item.active:hover .list-group-item-heading,
  .list-group-item.active:focus .list-group-item-heading,
  .list-group-item.active .list-group-item-heading > small,
  .list-group-item.active:hover .list-group-item-heading > small,
  .list-group-item.active:focus .list-group-item-heading > small,
  .list-group-item.active .list-group-item-heading > .small,
  .list-group-item.active:hover .list-group-item-heading > .small,
  .list-group-item.active:focus .list-group-item-heading > .small {
    color: inherit;
  }
  .list-group-item.active .list-group-item-text,
  .list-group-item.active:hover .list-group-item-text,
  .list-group-item.active:focus .list-group-item-text {
    color: #fff;
  }
  .list-group-item-success {
    color: #98d85b;
    background-color: transparent;
  }
  a.list-group-item-success {
    color: #98d85b;
  }
  a.list-group-item-success .list-group-item-heading {
    color: inherit;
  }
  a.list-group-item-success:hover,
  a.list-group-item-success:focus {
    color: #98d85b;
    background-color: rgba(0, 0, 0, 0);
  }
  a.list-group-item-success.active,
  a.list-group-item-success.active:hover,
  a.list-group-item-success.active:focus {
    color: #fff;
    background-color: #98d85b;
    border-color: #98d85b;
  }
  .list-group-item-info {
    color: #935eff;
    background-color: transparent;
  }
  a.list-group-item-info {
    color: #935eff;
  }
  a.list-group-item-info .list-group-item-heading {
    color: inherit;
  }
  a.list-group-item-info:hover,
  a.list-group-item-info:focus {
    color: #935eff;
    background-color: rgba(0, 0, 0, 0);
  }
  a.list-group-item-info.active,
  a.list-group-item-info.active:hover,
  a.list-group-item-info.active:focus {
    color: #fff;
    background-color: #935eff;
    border-color: #935eff;
  }
  .list-group-item-warning {
    color: #ffa00a;
    background-color: transparent;
  }
  a.list-group-item-warning {
    color: #ffa00a;
  }
  a.list-group-item-warning .list-group-item-heading {
    color: inherit;
  }
  a.list-group-item-warning:hover,
  a.list-group-item-warning:focus {
    color: #ffa00a;
    background-color: rgba(0, 0, 0, 0);
  }
  a.list-group-item-warning.active,
  a.list-group-item-warning.active:hover,
  a.list-group-item-warning.active:focus {
    color: #fff;
    background-color: #ffa00a;
    border-color: #ffa00a;
  }
  .list-group-item-danger {
    color: #ff5858;
    background-color: transparent;
  }
  a.list-group-item-danger {
    color: #ff5858;
  }
  a.list-group-item-danger .list-group-item-heading {
    color: inherit;
  }
  a.list-group-item-danger:hover,
  a.list-group-item-danger:focus {
    color: #ff5858;
    background-color: rgba(0, 0, 0, 0);
  }
  a.list-group-item-danger.active,
  a.list-group-item-danger.active:hover,
  a.list-group-item-danger.active:focus {
    color: #fff;
    background-color: #ff5858;
    border-color: #ff5858;
  }
  .list-group-item-heading {
    margin-top: 0;
    margin-bottom: 5px;
  }
  .list-group-item-text {
    margin-bottom: 0;
    line-height: 1.3;
  }
  .panel {
    margin-bottom: 20px;
    background-color: #fff;
    border: 1px solid transparent;
    border-radius: 4px;
    -webkit-box-shadow: 0 1px 1px rgba(0, 0, 0, .05);
            box-shadow: 0 1px 1px rgba(0, 0, 0, .05);
  }
  .panel-body {
    padding: 15px;
  }
  .panel-heading {
    padding: 10px 15px;
    border-bottom: 1px solid transparent;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
  }
  .panel-heading > .dropdown .dropdown-toggle {
    color: inherit;
  }
  .panel-title {
    margin-top: 0;
    margin-bottom: 0;
    font-size: 16px;
    color: inherit;
  }
  .panel-title > a {
    color: inherit;
  }
  .panel-footer {
    padding: 10px 15px;
    background-color: #f5f5f5;
    border-top: 1px solid #ddd;
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
  }
  .panel > .list-group,
  .panel > .panel-collapse > .list-group {
    margin-bottom: 0;
  }
  .panel > .list-group .list-group-item,
  .panel > .panel-collapse > .list-group .list-group-item {
    border-width: 1px 0;
    border-radius: 0;
  }
  .panel > .list-group:first-child .list-group-item:first-child,
  .panel > .panel-collapse > .list-group:first-child .list-group-item:first-child {
    border-top: 0;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
  }
  .panel > .list-group:last-child .list-group-item:last-child,
  .panel > .panel-collapse > .list-group:last-child .list-group-item:last-child {
    border-bottom: 0;
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
  }
  .panel-heading + .list-group .list-group-item:first-child {
    border-top-width: 0;
  }
  .list-group + .panel-footer {
    border-top-width: 0;
  }
  .panel > .table,
  .panel > .table-responsive > .table,
  .panel > .panel-collapse > .table {
    margin-bottom: 0;
  }
  .panel > .table caption,
  .panel > .table-responsive > .table caption,
  .panel > .panel-collapse > .table caption {
    padding-right: 15px;
    padding-left: 15px;
  }
  .panel > .table:first-child,
  .panel > .table-responsive:first-child > .table:first-child {
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
  }
  .panel > .table:first-child > thead:first-child > tr:first-child,
  .panel > .table-responsive:first-child > .table:first-child > thead:first-child > tr:first-child,
  .panel > .table:first-child > tbody:first-child > tr:first-child,
  .panel > .table-responsive:first-child > .table:first-child > tbody:first-child > tr:first-child {
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
  }
  .panel > .table:first-child > thead:first-child > tr:first-child td:first-child,
  .panel > .table-responsive:first-child > .table:first-child > thead:first-child > tr:first-child td:first-child,
  .panel > .table:first-child > tbody:first-child > tr:first-child td:first-child,
  .panel > .table-responsive:first-child > .table:first-child > tbody:first-child > tr:first-child td:first-child,
  .panel > .table:first-child > thead:first-child > tr:first-child th:first-child,
  .panel > .table-responsive:first-child > .table:first-child > thead:first-child > tr:first-child th:first-child,
  .panel > .table:first-child > tbody:first-child > tr:first-child th:first-child,
  .panel > .table-responsive:first-child > .table:first-child > tbody:first-child > tr:first-child th:first-child {
    border-top-left-radius: 3px;
  }
  .panel > .table:first-child > thead:first-child > tr:first-child td:last-child,
  .panel > .table-responsive:first-child > .table:first-child > thead:first-child > tr:first-child td:last-child,
  .panel > .table:first-child > tbody:first-child > tr:first-child td:last-child,
  .panel > .table-responsive:first-child > .table:first-child > tbody:first-child > tr:first-child td:last-child,
  .panel > .table:first-child > thead:first-child > tr:first-child th:last-child,
  .panel > .table-responsive:first-child > .table:first-child > thead:first-child > tr:first-child th:last-child,
  .panel > .table:first-child > tbody:first-child > tr:first-child th:last-child,
  .panel > .table-responsive:first-child > .table:first-child > tbody:first-child > tr:first-child th:last-child {
    border-top-right-radius: 3px;
  }
  .panel > .table:last-child,
  .panel > .table-responsive:last-child > .table:last-child {
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
  }
  .panel > .table:last-child > tbody:last-child > tr:last-child,
  .panel > .table-responsive:last-child > .table:last-child > tbody:last-child > tr:last-child,
  .panel > .table:last-child > tfoot:last-child > tr:last-child,
  .panel > .table-responsive:last-child > .table:last-child > tfoot:last-child > tr:last-child {
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
  }
  .panel > .table:last-child > tbody:last-child > tr:last-child td:first-child,
  .panel > .table-responsive:last-child > .table:last-child > tbody:last-child > tr:last-child td:first-child,
  .panel > .table:last-child > tfoot:last-child > tr:last-child td:first-child,
  .panel > .table-responsive:last-child > .table:last-child > tfoot:last-child > tr:last-child td:first-child,
  .panel > .table:last-child > tbody:last-child > tr:last-child th:first-child,
  .panel > .table-responsive:last-child > .table:last-child > tbody:last-child > tr:last-child th:first-child,
  .panel > .table:last-child > tfoot:last-child > tr:last-child th:first-child,
  .panel > .table-responsive:last-child > .table:last-child > tfoot:last-child > tr:last-child th:first-child {
    border-bottom-left-radius: 3px;
  }
  .panel > .table:last-child > tbody:last-child > tr:last-child td:last-child,
  .panel > .table-responsive:last-child > .table:last-child > tbody:last-child > tr:last-child td:last-child,
  .panel > .table:last-child > tfoot:last-child > tr:last-child td:last-child,
  .panel > .table-responsive:last-child > .table:last-child > tfoot:last-child > tr:last-child td:last-child,
  .panel > .table:last-child > tbody:last-child > tr:last-child th:last-child,
  .panel > .table-responsive:last-child > .table:last-child > tbody:last-child > tr:last-child th:last-child,
  .panel > .table:last-child > tfoot:last-child > tr:last-child th:last-child,
  .panel > .table-responsive:last-child > .table:last-child > tfoot:last-child > tr:last-child th:last-child {
    border-bottom-right-radius: 3px;
  }
  .panel > .panel-body + .table,
  .panel > .panel-body + .table-responsive,
  .panel > .table + .panel-body,
  .panel > .table-responsive + .panel-body {
    border-top: 1px solid #d1d8dd;
  }
  .panel > .table > tbody:first-child > tr:first-child th,
  .panel > .table > tbody:first-child > tr:first-child td {
    border-top: 0;
  }
  .panel > .table-bordered,
  .panel > .table-responsive > .table-bordered {
    border: 0;
  }
  .panel > .table-bordered > thead > tr > th:first-child,
  .panel > .table-responsive > .table-bordered > thead > tr > th:first-child,
  .panel > .table-bordered > tbody > tr > th:first-child,
  .panel > .table-responsive > .table-bordered > tbody > tr > th:first-child,
  .panel > .table-bordered > tfoot > tr > th:first-child,
  .panel > .table-responsive > .table-bordered > tfoot > tr > th:first-child,
  .panel > .table-bordered > thead > tr > td:first-child,
  .panel > .table-responsive > .table-bordered > thead > tr > td:first-child,
  .panel > .table-bordered > tbody > tr > td:first-child,
  .panel > .table-responsive > .table-bordered > tbody > tr > td:first-child,
  .panel > .table-bordered > tfoot > tr > td:first-child,
  .panel > .table-responsive > .table-bordered > tfoot > tr > td:first-child {
    border-left: 0;
  }
  .panel > .table-bordered > thead > tr > th:last-child,
  .panel > .table-responsive > .table-bordered > thead > tr > th:last-child,
  .panel > .table-bordered > tbody > tr > th:last-child,
  .panel > .table-responsive > .table-bordered > tbody > tr > th:last-child,
  .panel > .table-bordered > tfoot > tr > th:last-child,
  .panel > .table-responsive > .table-bordered > tfoot > tr > th:last-child,
  .panel > .table-bordered > thead > tr > td:last-child,
  .panel > .table-responsive > .table-bordered > thead > tr > td:last-child,
  .panel > .table-bordered > tbody > tr > td:last-child,
  .panel > .table-responsive > .table-bordered > tbody > tr > td:last-child,
  .panel > .table-bordered > tfoot > tr > td:last-child,
  .panel > .table-responsive > .table-bordered > tfoot > tr > td:last-child {
    border-right: 0;
  }
  .panel > .table-bordered > thead > tr:first-child > td,
  .panel > .table-responsive > .table-bordered > thead > tr:first-child > td,
  .panel > .table-bordered > tbody > tr:first-child > td,
  .panel > .table-responsive > .table-bordered > tbody > tr:first-child > td,
  .panel > .table-bordered > thead > tr:first-child > th,
  .panel > .table-responsive > .table-bordered > thead > tr:first-child > th,
  .panel > .table-bordered > tbody > tr:first-child > th,
  .panel > .table-responsive > .table-bordered > tbody > tr:first-child > th {
    border-bottom: 0;
  }
  .panel > .table-bordered > tbody > tr:last-child > td,
  .panel > .table-responsive > .table-bordered > tbody > tr:last-child > td,
  .panel > .table-bordered > tfoot > tr:last-child > td,
  .panel > .table-responsive > .table-bordered > tfoot > tr:last-child > td,
  .panel > .table-bordered > tbody > tr:last-child > th,
  .panel > .table-responsive > .table-bordered > tbody > tr:last-child > th,
  .panel > .table-bordered > tfoot > tr:last-child > th,
  .panel > .table-responsive > .table-bordered > tfoot > tr:last-child > th {
    border-bottom: 0;
  }
  .panel > .table-responsive {
    margin-bottom: 0;
    border: 0;
  }
  .panel-group {
    margin-bottom: 20px;
  }
  .panel-group .panel {
    margin-bottom: 0;
    border-radius: 4px;
  }
  .panel-group .panel + .panel {
    margin-top: 5px;
  }
  .panel-group .panel-heading {
    border-bottom: 0;
  }
  .panel-group .panel-heading + .panel-collapse > .panel-body,
  .panel-group .panel-heading + .panel-collapse > .list-group {
    border-top: 1px solid #ddd;
  }
  .panel-group .panel-footer {
    border-top: 0;
  }
  .panel-group .panel-footer + .panel-collapse .panel-body {
    border-bottom: 1px solid #ddd;
  }
  .panel-default {
    border-color: #ced5db;
  }
  .panel-default > .panel-heading {
    color: #333;
    background-color: #f7fafc;
    border-color: #ced5db;
  }
  .panel-default > .panel-heading + .panel-collapse > .panel-body {
    border-top-color: #ced5db;
  }
  .panel-default > .panel-heading .badge {
    color: #f7fafc;
    background-color: #333;
  }
  .panel-default > .panel-footer + .panel-collapse > .panel-body {
    border-bottom-color: #ced5db;
  }
  .panel-primary {
    border-color: #5e64ff;
  }
  .panel-primary > .panel-heading {
    color: #fff;
    background-color: #5e64ff;
    border-color: #5e64ff;
  }
  .panel-primary > .panel-heading + .panel-collapse > .panel-body {
    border-top-color: #5e64ff;
  }
  .panel-primary > .panel-heading .badge {
    color: #5e64ff;
    background-color: #fff;
  }
  .panel-primary > .panel-footer + .panel-collapse > .panel-body {
    border-bottom-color: #5e64ff;
  }
  .panel-success {
    border-color: rgba(0, 0, 0, 0);
  }
  .panel-success > .panel-heading {
    color: #98d85b;
    background-color: transparent;
    border-color: rgba(0, 0, 0, 0);
  }
  .panel-success > .panel-heading + .panel-collapse > .panel-body {
    border-top-color: rgba(0, 0, 0, 0);
  }
  .panel-success > .panel-heading .badge {
    color: transparent;
    background-color: #98d85b;
  }
  .panel-success > .panel-footer + .panel-collapse > .panel-body {
    border-bottom-color: rgba(0, 0, 0, 0);
  }
  .panel-info {
    border-color: rgba(0, 0, 0, 0);
  }
  .panel-info > .panel-heading {
    color: #935eff;
    background-color: transparent;
    border-color: rgba(0, 0, 0, 0);
  }
  .panel-info > .panel-heading + .panel-collapse > .panel-body {
    border-top-color: rgba(0, 0, 0, 0);
  }
  .panel-info > .panel-heading .badge {
    color: transparent;
    background-color: #935eff;
  }
  .panel-info > .panel-footer + .panel-collapse > .panel-body {
    border-bottom-color: rgba(0, 0, 0, 0);
  }
  .panel-warning {
    border-color: rgba(0, 0, 0, 0);
  }
  .panel-warning > .panel-heading {
    color: #ffa00a;
    background-color: transparent;
    border-color: rgba(0, 0, 0, 0);
  }
  .panel-warning > .panel-heading + .panel-collapse > .panel-body {
    border-top-color: rgba(0, 0, 0, 0);
  }
  .panel-warning > .panel-heading .badge {
    color: transparent;
    background-color: #ffa00a;
  }
  .panel-warning > .panel-footer + .panel-collapse > .panel-body {
    border-bottom-color: rgba(0, 0, 0, 0);
  }
  .panel-danger {
    border-color: rgba(0, 0, 0, 0);
  }
  .panel-danger > .panel-heading {
    color: #ff5858;
    background-color: transparent;
    border-color: rgba(0, 0, 0, 0);
  }
  .panel-danger > .panel-heading + .panel-collapse > .panel-body {
    border-top-color: rgba(0, 0, 0, 0);
  }
  .panel-danger > .panel-heading .badge {
    color: transparent;
    background-color: #ff5858;
  }
  .panel-danger > .panel-footer + .panel-collapse > .panel-body {
    border-bottom-color: rgba(0, 0, 0, 0);
  }
  .embed-responsive {
    position: relative;
    display: block;
    height: 0;
    padding: 0;
    overflow: hidden;
  }
  .embed-responsive .embed-responsive-item,
  .embed-responsive iframe,
  .embed-responsive embed,
  .embed-responsive object,
  .embed-responsive video {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 0;
  }
  .embed-responsive.embed-responsive-16by9 {
    padding-bottom: 56.25%;
  }
  .embed-responsive.embed-responsive-4by3 {
    padding-bottom: 75%;
  }
  .well {
    min-height: 20px;
    padding: 19px;
    margin-bottom: 20px;
    background-color: #fafbfc;
    border: 1px solid #d1d8dd;
    border-radius: 4px;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, .05);
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .05);
  }
  .well blockquote {
    border-color: #ddd;
    border-color: rgba(0, 0, 0, .15);
  }
  .well-lg {
    padding: 24px;
    border-radius: 6px;
  }
  .well-sm {
    padding: 9px;
    border-radius: 3px;
  }
  .close {
    float: right;
    font-size: 21px;
    font-weight: bold;
    line-height: 1;
    color: #000;
    text-shadow: 0 1px 0 #fff;
    filter: alpha(opacity=20);
    opacity: .2;
  }
  .close:hover,
  .close:focus {
    color: #000;
    text-decoration: none;
    cursor: pointer;
    filter: alpha(opacity=50);
    opacity: .5;
  }
  button.close {
    -webkit-appearance: none;
    padding: 0;
    cursor: pointer;
    background: transparent;
    border: 0;
  }
  .modal-open {
    overflow: hidden;
  }
  .modal {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 1040;
    display: none;
    overflow: hidden;
    -webkit-overflow-scrolling: touch;
    outline: 0;
  }
  .modal.fade .modal-dialog {
    -webkit-transition: -webkit-transform .3s ease-out;
         -o-transition:      -o-transform .3s ease-out;
            transition:         transform .3s ease-out;
    -webkit-transform: translate(0, -25%);
        -ms-transform: translate(0, -25%);
         -o-transform: translate(0, -25%);
            transform: translate(0, -25%);
  }
  .modal.in .modal-dialog {
    -webkit-transform: translate(0, 0);
        -ms-transform: translate(0, 0);
         -o-transform: translate(0, 0);
            transform: translate(0, 0);
  }
  .modal-open .modal {
    overflow-x: hidden;
    overflow-y: auto;
  }
  .modal-dialog {
    position: relative;
    width: auto;
    margin: 10px;
  }
  .modal-content {
    position: relative;
    background-color: #fff;
    -webkit-background-clip: padding-box;
            background-clip: padding-box;
    border: 1px solid #999;
    border: 1px solid rgba(0, 0, 0, .2);
    border-radius: 6px;
    outline: 0;
    -webkit-box-shadow: 0 3px 9px rgba(0, 0, 0, .5);
            box-shadow: 0 3px 9px rgba(0, 0, 0, .5);
  }
  .modal-backdrop {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    background-color: #334143;
  }
  .modal-backdrop.fade {
    filter: alpha(opacity=0);
    opacity: 0;
  }
  .modal-backdrop.in {
    filter: alpha(opacity=50);
    opacity: .5;
  }
  .modal-header {
    min-height: 16.42857143px;
    padding: 15px;
    border-bottom: 1px solid #e5e5e5;
  }
  .modal-header .close {
    margin-top: -2px;
  }
  .modal-title {
    margin: 0;
    line-height: 1.42857143;
  }
  .modal-body {
    position: relative;
    padding: 15px;
  }
  .modal-footer {
    padding: 15px;
    text-align: right;
    border-top: 1px solid #e5e5e5;
  }
  .modal-footer .btn + .btn {
    margin-bottom: 0;
    margin-left: 5px;
  }
  .modal-footer .btn-group .btn + .btn {
    margin-left: -1px;
  }
  .modal-footer .btn-block + .btn-block {
    margin-left: 0;
  }
  .modal-scrollbar-measure {
    position: absolute;
    top: -9999px;
    width: 50px;
    height: 50px;
    overflow: scroll;
  }
  @media (min-width: 768px) {
    .modal-dialog {
      width: 600px;
      margin: 30px auto;
    }
    .modal-content {
      -webkit-box-shadow: 0 5px 15px rgba(0, 0, 0, .5);
              box-shadow: 0 5px 15px rgba(0, 0, 0, .5);
    }
    .modal-sm {
      width: 300px;
    }
  }
  @media (min-width: 992px) {
    .modal-lg {
      width: 900px;
    }
  }
  .tooltip {
    position: absolute;
    z-index: 1070;
    display: block;
    font-family: 'Helvetica Neue', Helvetica, Arial, 'Open Sans', sans-serif;
    font-size: 12px;
    font-weight: normal;
    line-height: 1.4;
    visibility: visible;
    filter: alpha(opacity=0);
    opacity: 0;
  }
  .tooltip.in {
    filter: alpha(opacity=90);
    opacity: .9;
  }
  .tooltip.top {
    padding: 5px 0;
    margin-top: -3px;
  }
  .tooltip.right {
    padding: 0 5px;
    margin-left: 3px;
  }
  .tooltip.bottom {
    padding: 5px 0;
    margin-top: 3px;
  }
  .tooltip.left {
    padding: 0 5px;
    margin-left: -3px;
  }
  .tooltip-inner {
    max-width: 200px;
    padding: 3px 8px;
    color: #fff;
    text-align: center;
    text-decoration: none;
    background-color: #000;
    border-radius: 4px;
  }
  .tooltip-arrow {
    position: absolute;
    width: 0;
    height: 0;
    border-color: transparent;
    border-style: solid;
  }
  .tooltip.top .tooltip-arrow {
    bottom: 0;
    left: 50%;
    margin-left: -5px;
    border-width: 5px 5px 0;
    border-top-color: #000;
  }
  .tooltip.top-left .tooltip-arrow {
    right: 5px;
    bottom: 0;
    margin-bottom: -5px;
    border-width: 5px 5px 0;
    border-top-color: #000;
  }
  .tooltip.top-right .tooltip-arrow {
    bottom: 0;
    left: 5px;
    margin-bottom: -5px;
    border-width: 5px 5px 0;
    border-top-color: #000;
  }
  .tooltip.right .tooltip-arrow {
    top: 50%;
    left: 0;
    margin-top: -5px;
    border-width: 5px 5px 5px 0;
    border-right-color: #000;
  }
  .tooltip.left .tooltip-arrow {
    top: 50%;
    right: 0;
    margin-top: -5px;
    border-width: 5px 0 5px 5px;
    border-left-color: #000;
  }
  .tooltip.bottom .tooltip-arrow {
    top: 0;
    left: 50%;
    margin-left: -5px;
    border-width: 0 5px 5px;
    border-bottom-color: #000;
  }
  .tooltip.bottom-left .tooltip-arrow {
    top: 0;
    right: 5px;
    margin-top: -5px;
    border-width: 0 5px 5px;
    border-bottom-color: #000;
  }
  .tooltip.bottom-right .tooltip-arrow {
    top: 0;
    left: 5px;
    margin-top: -5px;
    border-width: 0 5px 5px;
    border-bottom-color: #000;
  }
  .popover {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1060;
    display: none;
    max-width: 276px;
    padding: 1px;
    font-family: 'Helvetica Neue', Helvetica, Arial, 'Open Sans', sans-serif;
    font-size: 14px;
    font-weight: normal;
    line-height: 1.42857143;
    text-align: left;
    white-space: normal;
    background-color: #fff;
    -webkit-background-clip: padding-box;
            background-clip: padding-box;
    border: 1px solid #ccc;
    border: 1px solid rgba(0, 0, 0, .2);
    border-radius: 6px;
    -webkit-box-shadow: 0 5px 10px rgba(0, 0, 0, .2);
            box-shadow: 0 5px 10px rgba(0, 0, 0, .2);
  }
  .popover.top {
    margin-top: -10px;
  }
  .popover.right {
    margin-left: 10px;
  }
  .popover.bottom {
    margin-top: 10px;
  }
  .popover.left {
    margin-left: -10px;
  }
  .popover-title {
    padding: 8px 14px;
    margin: 0;
    font-size: 14px;
    background-color: #f7f7f7;
    border-bottom: 1px solid #ebebeb;
    border-radius: 5px 5px 0 0;
  }
  .popover-content {
    padding: 9px 14px;
  }
  .popover > .arrow,
  .popover > .arrow:after {
    position: absolute;
    display: block;
    width: 0;
    height: 0;
    border-color: transparent;
    border-style: solid;
  }
  .popover > .arrow {
    border-width: 11px;
  }
  .popover > .arrow:after {
    content: '';
    border-width: 10px;
  }
  .popover.top > .arrow {
    bottom: -11px;
    left: 50%;
    margin-left: -11px;
    border-top-color: #999;
    border-top-color: rgba(0, 0, 0, .25);
    border-bottom-width: 0;
  }
  .popover.top > .arrow:after {
    bottom: 1px;
    margin-left: -10px;
    content: ' ';
    border-top-color: #fff;
    border-bottom-width: 0;
  }
  .popover.right > .arrow {
    top: 50%;
    left: -11px;
    margin-top: -11px;
    border-right-color: #999;
    border-right-color: rgba(0, 0, 0, .25);
    border-left-width: 0;
  }
  .popover.right > .arrow:after {
    bottom: -10px;
    left: 1px;
    content: ' ';
    border-right-color: #fff;
    border-left-width: 0;
  }
  .popover.bottom > .arrow {
    top: -11px;
    left: 50%;
    margin-left: -11px;
    border-top-width: 0;
    border-bottom-color: #999;
    border-bottom-color: rgba(0, 0, 0, .25);
  }
  .popover.bottom > .arrow:after {
    top: 1px;
    margin-left: -10px;
    content: ' ';
    border-top-width: 0;
    border-bottom-color: #fff;
  }
  .popover.left > .arrow {
    top: 50%;
    right: -11px;
    margin-top: -11px;
    border-right-width: 0;
    border-left-color: #999;
    border-left-color: rgba(0, 0, 0, .25);
  }
  .popover.left > .arrow:after {
    right: 1px;
    bottom: -10px;
    content: ' ';
    border-right-width: 0;
    border-left-color: #fff;
  }
  .carousel {
    position: relative;
  }
  .carousel-inner {
    position: relative;
    width: 100%;
    overflow: hidden;
  }
  .carousel-inner > .item {
    position: relative;
    display: none;
    -webkit-transition: .6s ease-in-out left;
         -o-transition: .6s ease-in-out left;
            transition: .6s ease-in-out left;
  }
  .carousel-inner > .item > img,
  .carousel-inner > .item > a > img {
    line-height: 1;
  }
  @media all and (transform-3d), (-webkit-transform-3d) {
    .carousel-inner > .item {
      -webkit-transition: -webkit-transform .6s ease-in-out;
           -o-transition:      -o-transform .6s ease-in-out;
              transition:         transform .6s ease-in-out;
  
      -webkit-backface-visibility: hidden;
              backface-visibility: hidden;
      -webkit-perspective: 1000;
              perspective: 1000;
    }
    .carousel-inner > .item.next,
    .carousel-inner > .item.active.right {
      left: 0;
      -webkit-transform: translate3d(100%, 0, 0);
              transform: translate3d(100%, 0, 0);
    }
    .carousel-inner > .item.prev,
    .carousel-inner > .item.active.left {
      left: 0;
      -webkit-transform: translate3d(-100%, 0, 0);
              transform: translate3d(-100%, 0, 0);
    }
    .carousel-inner > .item.next.left,
    .carousel-inner > .item.prev.right,
    .carousel-inner > .item.active {
      left: 0;
      -webkit-transform: translate3d(0, 0, 0);
              transform: translate3d(0, 0, 0);
    }
  }
  .carousel-inner > .active,
  .carousel-inner > .next,
  .carousel-inner > .prev {
    display: block;
  }
  .carousel-inner > .active {
    left: 0;
  }
  .carousel-inner > .next,
  .carousel-inner > .prev {
    position: absolute;
    top: 0;
    width: 100%;
  }
  .carousel-inner > .next {
    left: 100%;
  }
  .carousel-inner > .prev {
    left: -100%;
  }
  .carousel-inner > .next.left,
  .carousel-inner > .prev.right {
    left: 0;
  }
  .carousel-inner > .active.left {
    left: -100%;
  }
  .carousel-inner > .active.right {
    left: 100%;
  }
  .carousel-control {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    width: 15%;
    font-size: 20px;
    color: #fff;
    text-align: center;
    text-shadow: 0 1px 2px rgba(0, 0, 0, .6);
    filter: alpha(opacity=50);
    opacity: .5;
  }
  .carousel-control.left {
    background-image: -webkit-linear-gradient(left, rgba(0, 0, 0, .5) 0%, rgba(0, 0, 0, .0001) 100%);
    background-image:      -o-linear-gradient(left, rgba(0, 0, 0, .5) 0%, rgba(0, 0, 0, .0001) 100%);
    background-image: -webkit-gradient(linear, left top, right top, from(rgba(0, 0, 0, .5)), to(rgba(0, 0, 0, .0001)));
    background-image:         linear-gradient(to right, rgba(0, 0, 0, .5) 0%, rgba(0, 0, 0, .0001) 100%);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#80000000', endColorstr='#00000000', GradientType=1);
    background-repeat: repeat-x;
  }
  .carousel-control.right {
    right: 0;
    left: auto;
    background-image: -webkit-linear-gradient(left, rgba(0, 0, 0, .0001) 0%, rgba(0, 0, 0, .5) 100%);
    background-image:      -o-linear-gradient(left, rgba(0, 0, 0, .0001) 0%, rgba(0, 0, 0, .5) 100%);
    background-image: -webkit-gradient(linear, left top, right top, from(rgba(0, 0, 0, .0001)), to(rgba(0, 0, 0, .5)));
    background-image:         linear-gradient(to right, rgba(0, 0, 0, .0001) 0%, rgba(0, 0, 0, .5) 100%);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#00000000', endColorstr='#80000000', GradientType=1);
    background-repeat: repeat-x;
  }
  .carousel-control:hover,
  .carousel-control:focus {
    color: #fff;
    text-decoration: none;
    filter: alpha(opacity=90);
    outline: 0;
    opacity: .9;
  }
  .carousel-control .icon-prev,
  .carousel-control .icon-next,
  .carousel-control .glyphicon-chevron-left,
  .carousel-control .glyphicon-chevron-right {
    position: absolute;
    top: 50%;
    z-index: 5;
    display: inline-block;
  }
  .carousel-control .icon-prev,
  .carousel-control .glyphicon-chevron-left {
    left: 50%;
    margin-left: -10px;
  }
  .carousel-control .icon-next,
  .carousel-control .glyphicon-chevron-right {
    right: 50%;
    margin-right: -10px;
  }
  .carousel-control .icon-prev,
  .carousel-control .icon-next {
    width: 20px;
    height: 20px;
    margin-top: -10px;
    font-family: serif;
    line-height: 1;
  }

  .carousel-indicators {
    position: absolute;
    bottom: 10px;
    left: 50%;
    z-index: 15;
    width: 60%;
    padding-left: 0;
    margin-left: -30%;
    text-align: center;
    list-style: none;
  }
  .carousel-indicators li {
    display: inline-block;
    width: 10px;
    height: 10px;
    margin: 1px;
    text-indent: -999px;
    cursor: pointer;
    background-color: #000;
    background-color: rgba(0, 0, 0, 0);
    border: 1px solid #fff;
    border-radius: 10px;
  }
  .carousel-indicators .active {
    width: 12px;
    height: 12px;
    margin: 0;
    background-color: #fff;
  }
  .carousel-caption {
    position: absolute;
    right: 15%;
    bottom: 20px;
    left: 15%;
    z-index: 10;
    padding-top: 20px;
    padding-bottom: 20px;
    color: #fff;
    text-align: center;
    text-shadow: 0 1px 2px rgba(0, 0, 0, .6);
  }
  .carousel-caption .btn {
    text-shadow: none;
  }
  @media screen and (min-width: 768px) {
    .carousel-control .glyphicon-chevron-left,
    .carousel-control .glyphicon-chevron-right,
    .carousel-control .icon-prev,
    .carousel-control .icon-next {
      width: 30px;
      height: 30px;
      margin-top: -15px;
      font-size: 30px;
    }
    .carousel-control .glyphicon-chevron-left,
    .carousel-control .icon-prev {
      margin-left: -15px;
    }
    .carousel-control .glyphicon-chevron-right,
    .carousel-control .icon-next {
      margin-right: -15px;
    }
    .carousel-caption {
      right: 20%;
      left: 20%;
      padding-bottom: 30px;
    }
    .carousel-indicators {
      bottom: 20px;
    }
  }
  .clearfix:before,
  .clearfix:after,
  .dl-horizontal dd:before,
  .dl-horizontal dd:after,
  .container:before,
  .container:after,
  .container-fluid:before,
  .container-fluid:after,
  .row:before,
  .row:after,
  .form-horizontal .form-group:before,
  .form-horizontal .form-group:after,
  .btn-toolbar:before,
  .btn-toolbar:after,
  .btn-group-vertical > .btn-group:before,
  .btn-group-vertical > .btn-group:after,
  .nav:before,
  .nav:after,
  .navbar:before,
  .navbar:after,
  .navbar-header:before,
  .navbar-header:after,
  .navbar-collapse:before,
  .navbar-collapse:after,
  .pager:before,
  .pager:after,
  .panel-body:before,
  .panel-body:after,
  .modal-footer:before,
  .modal-footer:after {
    display: table;
    content: ' ';
  }
  .clearfix:after,
  .dl-horizontal dd:after,
  .container:after,
  .container-fluid:after,
  .row:after,
  .form-horizontal .form-group:after,
  .btn-toolbar:after,
  .btn-group-vertical > .btn-group:after,
  .nav:after,
  .navbar:after,
  .navbar-header:after,
  .navbar-collapse:after,
  .pager:after,
  .panel-body:after,
  .modal-footer:after {
    clear: both;
  }
  .center-block {
    display: block;
    margin-right: auto;
    margin-left: auto;
  }
  .pull-right {
    float: right !important;
  }
  .pull-left {
    float: left !important;
  }
  .hide {
    display: none !important;
  }
  .show {
    display: block !important;
  }
  .invisible {
    visibility: hidden;
  }
  .text-hide {
    font: 0/0 a;
    color: transparent;
    text-shadow: none;
    background-color: transparent;
    border: 0;
  }
  .hidden {
    display: none !important;
    visibility: hidden !important;
  }
  .affix {
    position: fixed;
  }
  @-ms-viewport {
    width: device-width;
  }
  .visible-xs,
  .visible-sm,
  .visible-md,
  .visible-lg {
    display: none !important;
  }
  .visible-xs-block,
  .visible-xs-inline,
  .visible-xs-inline-block,
  .visible-sm-block,
  .visible-sm-inline,
  .visible-sm-inline-block,
  .visible-md-block,
  .visible-md-inline,
  .visible-md-inline-block,
  .visible-lg-block,
  .visible-lg-inline,
  .visible-lg-inline-block {
    display: none !important;
  }
  @media (max-width: 767px) {
    .visible-xs {
      display: block !important;
    }
    table.visible-xs {
      display: table;
    }
    tr.visible-xs {
      display: table-row !important;
    }
    th.visible-xs,
    td.visible-xs {
      display: table-cell !important;
    }
  }
  @media (max-width: 767px) {
    .visible-xs-block {
      display: block !important;
    }
  }
  @media (max-width: 767px) {
    .visible-xs-inline {
      display: inline !important;
    }
  }
  @media (max-width: 767px) {
    .visible-xs-inline-block {
      display: inline-block !important;
    }
  }
  @media (min-width: 768px) and (max-width: 991px) {
    .visible-sm {
      display: block !important;
    }
    table.visible-sm {
      display: table;
    }
    tr.visible-sm {
      display: table-row !important;
    }
    th.visible-sm,
    td.visible-sm {
      display: table-cell !important;
    }
  }
  @media (min-width: 768px) and (max-width: 991px) {
    .visible-sm-block {
      display: block !important;
    }
  }
  @media (min-width: 768px) and (max-width: 991px) {
    .visible-sm-inline {
      display: inline !important;
    }
  }
  @media (min-width: 768px) and (max-width: 991px) {
    .visible-sm-inline-block {
      display: inline-block !important;
    }
  }
  @media (min-width: 992px) and (max-width: 1199px) {
    .visible-md {
      display: block !important;
    }
    table.visible-md {
      display: table;
    }
    tr.visible-md {
      display: table-row !important;
    }
    th.visible-md,
    td.visible-md {
      display: table-cell !important;
    }
  }
  @media (min-width: 992px) and (max-width: 1199px) {
    .visible-md-block {
      display: block !important;
    }
  }
  @media (min-width: 992px) and (max-width: 1199px) {
    .visible-md-inline {
      display: inline !important;
    }
  }
  @media (min-width: 992px) and (max-width: 1199px) {
    .visible-md-inline-block {
      display: inline-block !important;
    }
  }
  @media (min-width: 1200px) {
    .visible-lg {
      display: block !important;
    }
    table.visible-lg {
      display: table;
    }
    tr.visible-lg {
      display: table-row !important;
    }
    th.visible-lg,
    td.visible-lg {
      display: table-cell !important;
    }
  }
  @media (min-width: 1200px) {
    .visible-lg-block {
      display: block !important;
    }
  }
  @media (min-width: 1200px) {
    .visible-lg-inline {
      display: inline !important;
    }
  }
  @media (min-width: 1200px) {
    .visible-lg-inline-block {
      display: inline-block !important;
    }
  }
  @media (max-width: 767px) {
    .hidden-xs {
      display: none !important;
    }
  }
  @media (min-width: 768px) and (max-width: 991px) {
    .hidden-sm {
      display: none !important;
    }
  }
  @media (min-width: 992px) and (max-width: 1199px) {
    .hidden-md {
      display: none !important;
    }
  }
  @media (min-width: 1200px) {
    .hidden-lg {
      display: none !important;
    }
  }
  .visible-print {
    display: none !important;
  }
  @media print {
    .visible-print {
      display: block !important;
    }
    table.visible-print {
      display: table;
    }
    tr.visible-print {
      display: table-row !important;
    }
    th.visible-print,
    td.visible-print {
      display: table-cell !important;
    }
  }
  .visible-print-block {
    display: none !important;
  }
  @media print {
    .visible-print-block {
      display: block !important;
    }
  }
  .visible-print-inline {
    display: none !important;
  }
  @media print {
    .visible-print-inline {
      display: inline !important;
    }
  }
  .visible-print-inline-block {
    display: none !important;
  }
  @media print {
    .visible-print-inline-block {
      display: inline-block !important;
    }
  }
  @media print {
    .hidden-print {
      display: none !important;
    }
  }
  body {
    text-rendering: optimizeLegibility;
  }
  .list-group-item {
    padding: 8px 15px;
  }
  h3,
  h4 {
    font-weight: bold;
  }
  ul.with-margin li,
  ol.with-margin li {
    margin: 7px auto;
  }
  .form-control,
  .btn:active,
  .btn:focus,
  .btn.active,
  .btn-group .dropdown-toggle:active,
  .btn-group.open .dropdown-toggle {
    -webkit-box-shadow: none;
            box-shadow: none;
  }
  a {
    cursor: pointer;
  }
  a:hover,
  a:focus {
    text-decoration: underline;
  }
  .navbar a:hover,
  .navbar a:focus,
  .dropdown-menu a:hover,
  .dropdown-menu a:focus {
    border-bottom: none;
  }
  h4.modal-title {
    font-weight: normal;
  }
  .modal-content {
    border-radius: 3px;
  }
  .navbar-inverse .form-control {
    color: #b8c2cb;
    background-color: #475765;
    border: 1px solid #475765;
  }
  .navbar-inverse .form-control::-webkit-input-placeholder {
    color: #b8c2cb;
  }
  .navbar-inverse .form-control::-moz-placeholder {
    color: #b8c2cb;
  }
  .navbar-inverse .form-control:-ms-input-placeholder {
    color: #b8c2cb;
  }
  .navbar-inverse .form-control:focus {
    -webkit-box-shadow: none;
            box-shadow: none;
  }
  .navbar-search-icon {
    color: #b8c2cb;
  }
"""