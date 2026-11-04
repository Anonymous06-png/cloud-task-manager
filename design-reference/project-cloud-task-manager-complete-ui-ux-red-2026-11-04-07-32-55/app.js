'use strict';
const $ = (s, root=document) => root.querySelector(s);
const icon = (name, cls='') => `<svg class="icon ${cls}" aria-hidden="true"><use href="assets/icons.svg#${name}"></use></svg>`;
const esc = str => String(str ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const dictionary = {
 vi:{workspace:'Không gian làm việc',personal:'Cá nhân',navigation:'Không gian của bạn',overview:'Tổng quan',tasks:'Công việc',completed:'Đã hoàn thành',settings:'Cài đặt',library:'Thư viện giao diện',collapse:'Thu gọn thanh bên',expand:'Mở rộng thanh bên',account:'Tài khoản',create:'Tạo công việc',overviewSub:'Thứ tư, 04 tháng 11 · Những việc cần chú ý hôm nay.',tasksSub:'Mọi việc cần làm, gọn trong một danh sách.',completedSub:'Những việc đã xong. Thêm chỗ cho việc tiếp theo.',settingsSub:'Một không gian làm việc theo cách của bạn.',librarySub:'Thành phần và trạng thái dùng chung trong toàn bộ giao diện.',open:'Chưa hoàn thành',upcoming:'Sắp đến hạn',done:'Đã hoàn thành',openSub:'Trong danh sách của bạn',upcomingSub:'Trong 7 ngày tới',doneSub:'Trong danh sách của bạn',priorities:'Việc cần ưu tiên',allTasks:'Xem tất cả',attention:'Cần chú ý',next:'Tiếp theo',overdue:'Quá hạn',today:'Hôm nay',tomorrow:'Ngày mai',friday:'Thứ sáu',noDate:'Chưa có hạn',noTime:'Không đặt giờ',high:'Ưu tiên',normal:'Bình thường',taskAction:'Thao tác công việc',completeAction:'Đánh dấu hoàn thành',reopenAction:'Đánh dấu chưa hoàn thành',smallSteps:'Từng việc một, nhẹ đầu hơn.',todayMessage:'Bạn có 1 công việc đến hạn hôm nay. Bắt đầu từ việc quan trọng nhất.',todayClear:'Hôm nay đã gọn hơn.',todayClearMessage:'Không còn công việc đến hạn hôm nay.',viewTask:'Mở công việc',week:'Những ngày tới',recent:'Vừa hoàn thành',viewCompleted:'Xem đã hoàn thành',recentDate:'Hoàn thành ngày',footer:'Không gian cá nhân',sample:'Bản xem trước · Dữ liệu mẫu',all:'Tất cả',incomplete:'Chưa xong',finished:'Đã xong',search:'Tìm công việc…',searchLabel:'Tìm công việc',task:'Công việc',status:'Trạng thái',due:'Hạn chót',showing:'Hiển thị',of:'trong',taskUnit:'công việc',noResults:'Không tìm thấy công việc',noResultsSub:'Thử từ khóa khác hoặc xóa bộ lọc để xem lại danh sách.',clearSearch:'Xóa tìm kiếm',emptyTitle:'Danh sách đang trống',emptySub:'Thêm một việc bạn muốn hoàn thành. Bạn có thể đặt hạn chót sau.',emptyCompleted:'Chưa có công việc hoàn thành',emptyCompletedSub:'Những việc bạn đánh dấu hoàn thành sẽ xuất hiện ở đây.',edit:'Chỉnh sửa',delete:'Xóa công việc',createTitle:'Tạo công việc mới',editTitle:'Chỉnh sửa công việc',taskName:'Tên công việc',namePlaceholder:'Bạn cần làm gì?',nameHint:'Một tên rõ ràng sẽ giúp bạn dễ bắt đầu.',notes:'Ghi chú',optional:'không bắt buộc',notesPlaceholder:'Thêm thông tin để bạn dễ bắt tay vào làm…',time:'Giờ nhắc việc',timeLabel:'Giờ đến hạn',priority:'Mức ưu tiên',cancel:'Hủy',save:'Lưu thay đổi',nameError:'Nhập tên công việc trước khi lưu.',nameLong:'Tên công việc không được dài quá 160 ký tự.',dateError:'Chọn hạn chót trước khi đặt giờ.',deleteTitle:'Xóa công việc này?',deleteWarning:'Công việc sẽ bị xóa khỏi danh sách. Bạn không thể hoàn tác thao tác này.',keepTask:'Giữ công việc',created:'Đã tạo công việc',updated:'Đã lưu thay đổi',deleted:'Đã xóa công việc',markedDone:'Đã đánh dấu hoàn thành',markedOpen:'Đã chuyển về chưa hoàn thành',language:'Ngôn ngữ',languageSub:'Ngôn ngữ hiển thị trong không gian của bạn.',vietnamese:'Tiếng Việt',english:'Tiếng Anh',langViDesc:'Hiển thị giao diện bằng tiếng Việt',langEnDesc:'Hiển thị giao diện bằng tiếng Anh',appearance:'Giao diện',appearanceSub:'Chọn nền phù hợp với cách bạn tập trung.',light:'Sáng',dark:'Tối',lightSub:'Nền sáng, rõ ràng và nhẹ mắt',darkSub:'Nền tối, dịu hơn trong ánh sáng yếu',sidebar:'Thanh điều hướng',sidebarSub:'Điều chỉnh không gian dành cho danh sách.',expanded:'Mở rộng',collapsed:'Thu gọn',expandedSub:'Biểu tượng và nhãn điều hướng',collapsedSub:'Chỉ biểu tượng, nhãn hiện khi rê chuột',autoSaved:'Lựa chọn được lưu trên trình duyệt này.',displayName:'Tên hiển thị',email:'Email',currentLanguage:'Ngôn ngữ hiện tại',signout:'Đăng xuất',signin:'Đăng nhập',register:'Tạo tài khoản',loginHeading:'Chào bạn trở lại.',loginSub:'Đăng nhập để tiếp tục những việc đang làm.',registerHeading:'Dành chỗ cho việc quan trọng.',registerSub:'Tạo tài khoản để sắp xếp công việc của riêng bạn.',password:'Mật khẩu',confirmPassword:'Nhập lại mật khẩu',passwordHint:'Ít nhất 8 ký tự.',remember:'Ghi nhớ đăng nhập',noAccount:'Chưa có tài khoản?',hasAccount:'Đã có tài khoản?',logoutHeading:'Bạn đã đăng xuất.',logoutSub:'Khi sẵn sàng, đăng nhập lại để tiếp tục công việc.',demoNotice:'Bản thiết kế tương tác. Thông tin đăng nhập không được gửi hoặc lưu.',demoContinue:'Xem không gian mẫu',authError:'Kiểm tra các trường được đánh dấu bên dưới.',emailError:'Nhập địa chỉ email hợp lệ, ví dụ ban@example.com.',passwordError:'Nhập mật khẩu có ít nhất 8 ký tự.',confirmError:'Mật khẩu nhập lại chưa khớp.',authDemo:'Đây là bản thiết kế. Chọn “Xem không gian mẫu” để tiếp tục.',nameRequired:'Nhập tên hiển thị của bạn.',showPassword:'Hiện mật khẩu',hidePassword:'Ẩn mật khẩu',preview:'Xem trước',colorSystem:'Màu sắc',typography:'Kiểu chữ',controls:'Nút và điều khiển',formStates:'Trạng thái biểu mẫu',screenStates:'Màn hình và trạng thái',interaction:'Quy tắc tương tác',backApp:'Về tổng quan',emptyPreview:'Danh sách trống',errorPreview:'Lỗi biểu mẫu',deletePreview:'Xác nhận xóa',authScreens:'Đăng nhập và đăng ký',defaultState:'Mặc định',hoverState:'Rê chuột',focusState:'Bàn phím',disabledState:'Vô hiệu hóa',state:'Trạng thái',behavior:'Cách thể hiện',close:'Đóng',menu:'Mở điều hướng',savedPreference:'Đã lưu lựa chọn',total:'Tổng cộng',back:'Quay lại',noUpcoming:'Chưa có hạn chót sắp tới',noUpcomingSub:'Các công việc có hạn trong 7 ngày tới sẽ xuất hiện ở đây.',resetDemo:'Đặt lại dữ liệu mẫu',checked:'Đã chọn',notRequired:'Tùy chọn',review:'Xem lại',confirm:'Xác nhận',progress:'Đang thực hiện',logoutNotice:'Bạn có thể đăng nhập lại bất cứ lúc nào.'},
 en:{workspace:'Your workspace',personal:'Personal',navigation:'Your space',overview:'Overview',tasks:'Tasks',completed:'Completed',settings:'Settings',library:'UI library',collapse:'Collapse sidebar',expand:'Expand sidebar',account:'Account',create:'Create task',overviewSub:'Wednesday, November 4 · Your work at a glance.',tasksSub:'Everything to do, in one clear list.',completedSub:'Finished work. More room for what comes next.',settingsSub:'A workspace that works your way.',librarySub:'Shared components and states across the entire interface.',open:'Incomplete',upcoming:'Due soon',done:'Completed',openSub:'In your task list',upcomingSub:'In the next 7 days',doneSub:'In your task list',priorities:'Your priorities',allTasks:'View all',attention:'Needs attention',next:'Up next',overdue:'Overdue',today:'Today',tomorrow:'Tomorrow',friday:'Friday',noDate:'No due date',noTime:'No time set',high:'Priority',normal:'Normal',taskAction:'Task actions',completeAction:'Mark complete',reopenAction:'Mark incomplete',smallSteps:'One task at a time.',todayMessage:'You have 1 task due today. Start with what matters most.',todayClear:'A little more room today.',todayClearMessage:'No more tasks are due today.',viewTask:'Open task',week:'Coming up',recent:'Recently completed',viewCompleted:'View completed',recentDate:'Completed on',footer:'Personal workspace',sample:'Design preview · Sample data',all:'All',incomplete:'Incomplete',finished:'Completed',search:'Search tasks…',searchLabel:'Search tasks',task:'Task',status:'Status',due:'Due date',showing:'Showing',of:'of',taskUnit:'tasks',noResults:'No tasks found',noResultsSub:'Try another keyword or clear the search to see your list.',clearSearch:'Clear search',emptyTitle:'A little room to begin',emptySub:'Add something you want to finish. You can set a due date later.',emptyCompleted:'No completed tasks yet',emptyCompletedSub:'Tasks you mark complete will appear here.',edit:'Edit task',delete:'Delete task',createTitle:'Create a new task',editTitle:'Edit task',taskName:'Task name',namePlaceholder:'What do you need to do?',nameHint:'A clear name makes it easier to begin.',notes:'Notes',optional:'optional',notesPlaceholder:'Add a little context to help you get started…',time:'Reminder time',timeLabel:'Due time',priority:'Priority',cancel:'Cancel',save:'Save changes',nameError:'Enter a task name before saving.',nameLong:'Keep the task name under 160 characters.',dateError:'Choose a due date before setting a time.',deleteTitle:'Delete this task?',deleteWarning:'This task will be removed from your list. This action cannot be undone.',keepTask:'Keep task',created:'Task created',updated:'Changes saved',deleted:'Task deleted',markedDone:'Marked complete',markedOpen:'Marked incomplete',language:'Language',languageSub:'The display language for your workspace.',vietnamese:'Vietnamese',english:'English',langViDesc:'Display the interface in Vietnamese',langEnDesc:'Display the interface in English',appearance:'Appearance',appearanceSub:'Choose the background that helps you focus.',light:'Light',dark:'Dark',lightSub:'A bright, clear workspace',darkSub:'A softer background in low light',sidebar:'Navigation',sidebarSub:'Adjust the space available for your tasks.',expanded:'Expanded',collapsed:'Collapsed',expandedSub:'Navigation icons and labels',collapsedSub:'Icons only, with labels on hover',autoSaved:'Preferences are saved in this browser.',displayName:'Display name',email:'Email',currentLanguage:'Current language',signout:'Sign out',signin:'Sign in',register:'Create account',loginHeading:'Welcome back.',loginSub:'Sign in to pick up where you left off.',registerHeading:'Make room for what matters.',registerSub:'Create an account to organize your own work.',password:'Password',confirmPassword:'Confirm password',passwordHint:'At least 8 characters.',remember:'Remember me',noAccount:'New here?',hasAccount:'Already have an account?',logoutHeading:'You’re signed out.',logoutSub:'When you’re ready, sign in to continue your work.',demoNotice:'Interactive design preview. Credentials are never sent or saved.',demoContinue:'Explore sample workspace',authError:'Check the highlighted fields below.',emailError:'Enter a valid email address, such as you@example.com.',passwordError:'Enter a password with at least 8 characters.',confirmError:'The passwords do not match.',authDemo:'This is a design preview. Choose “Explore sample workspace” to continue.',nameRequired:'Enter your display name.',showPassword:'Show password',hidePassword:'Hide password',preview:'Preview',colorSystem:'Color roles',typography:'Typography',controls:'Buttons and controls',formStates:'Form states',screenStates:'Screens and states',interaction:'Interaction guidelines',backApp:'Back to overview',emptyPreview:'Empty task list',errorPreview:'Form validation',deletePreview:'Delete confirmation',authScreens:'Sign in and registration',defaultState:'Default',hoverState:'Hover',focusState:'Keyboard focus',disabledState:'Disabled',state:'State',behavior:'Appearance',close:'Close',menu:'Open navigation',savedPreference:'Preference saved',total:'Total',back:'Back',noUpcoming:'No upcoming deadlines',noUpcomingSub:'Tasks due in the next 7 days will appear here.',resetDemo:'Reset sample data',checked:'Selected',notRequired:'Optional',review:'Review',confirm:'Confirm',progress:'In progress',logoutNotice:'You can sign back in at any time.'}
};

Object.assign(dictionary.vi,{description:'Mô tả',descriptionPlaceholder:'Thêm thông tin để bạn dễ bắt đầu…',descriptionHint:'Tùy chọn. Thêm bối cảnh, nội dung cần chuẩn bị hoặc kết quả mong muốn.',descriptionEmpty:'Chưa có mô tả',titleCount:'Tên ngắn gọn, dễ nhận biết.',completion:'Tình trạng hoàn thành',completionHelp:'Bạn có thể mở lại công việc bất cứ lúc nào.',dueHelp:'Để trống nếu công việc chưa có hạn chót.',formIntro:'Một việc rõ ràng, một bước tiếp theo.',loading:'Đang tải công việc…',loadingSub:'Danh sách công việc đang được cập nhật.',loadError:'Chưa tải được danh sách',loadErrorSub:'Hãy thử lại. Công việc của bạn không bị thay đổi.',retry:'Thử lại',saveError:'Chưa lưu được công việc. Nội dung bạn nhập vẫn được giữ lại.',saving:'Đang lưu…',saved:'Đã lưu công việc',savingHelp:'Đang lưu thay đổi của bạn.',successFeedback:'Phản hồi thành công',errorFeedback:'Phản hồi lỗi',screenDirectory:'Danh mục màn hình',screenDirectorySub:'Mỗi trạng thái sử dụng cùng hệ màu, kiểu chữ và thành phần của Tổng quan.',taskScreens:'Danh sách và trạng thái',formScreens:'Biểu mẫu công việc',accessScreens:'Tài khoản và đăng nhập',preferenceScreens:'Thiết lập cá nhân',allTasksLabel:'Tất cả công việc',firstPage:'Trang đầu',previousPage:'Trang trước',nextPage:'Trang sau',page:'Trang',savedDemo:'Đã lưu trong bản xem trước',username:'Tên đăng nhập',usernameHint:'Dùng tên này để đăng nhập vào tài khoản của bạn.',usernamePlaceholder:'minhanh',usernameError:'Nhập tên đăng nhập của bạn.',loginError:'Tên đăng nhập hoặc mật khẩu chưa đúng. Kiểm tra và thử lại.',registrationError:'Tên đăng nhập này đã được sử dụng. Hãy chọn một tên khác.',authLoading:'Đang đăng nhập…',registerLoading:'Đang tạo tài khoản…',registerSuccess:'Tài khoản đã được tạo.',registerSuccessSub:'Bạn có thể đăng nhập để bắt đầu thêm công việc.',passwordRequired:'Nhập mật khẩu của bạn.',descriptionSearch:'Tìm theo tên hoặc mô tả',loadingPreview:'Đang tải danh sách',listErrorPreview:'Lỗi tải danh sách',saveErrorPreview:'Lỗi lưu công việc',savingPreview:'Đang lưu công việc',successPreview:'Đã lưu công việc',authErrorPreview:'Thông tin đăng nhập chưa đúng',registrationSuccessPreview:'Tạo tài khoản thành công',backendScope:'Tên, mô tả, hạn chót và trạng thái hoàn thành.',taskCount:'Công việc của bạn',dateFormat:'Ngày / tháng / năm',selectedState:'Đã chọn',pendingState:'Đang xử lý',successState:'Thành công'});
Object.assign(dictionary.en,{description:'Description',descriptionPlaceholder:'Add a little context to help you begin…',descriptionHint:'Optional. Add context, preparation notes or the outcome you need.',descriptionEmpty:'No description yet',titleCount:'Keep the name clear and easy to recognize.',completion:'Completion status',completionHelp:'You can reopen this task at any time.',dueHelp:'Leave blank if there is no deadline yet.',formIntro:'One clear task. One next step.',loading:'Loading your tasks…',loadingSub:'Your task list is being updated.',loadError:'Your tasks couldn’t be loaded',loadErrorSub:'Try again. Your tasks have not been changed.',retry:'Try again',saveError:'Your task couldn’t be saved. Your entered details have been kept.',saving:'Saving…',saved:'Task saved',savingHelp:'Your changes are being saved.',successFeedback:'Success feedback',errorFeedback:'Error feedback',screenDirectory:'Screen directory',screenDirectorySub:'Every state uses the Overview’s colors, typography and shared components.',taskScreens:'Task list and states',formScreens:'Task forms',accessScreens:'Account access',preferenceScreens:'Personal settings',allTasksLabel:'All tasks',firstPage:'First page',previousPage:'Previous page',nextPage:'Next page',page:'Page',savedDemo:'Saved in this preview',username:'Username',usernameHint:'Use this name to sign in to your account.',usernamePlaceholder:'minhanh',usernameError:'Enter your username.',loginError:'The username or password is incorrect. Check your details and try again.',registrationError:'This username is already in use. Choose another name.',authLoading:'Signing in…',registerLoading:'Creating account…',registerSuccess:'Your account has been created.',registerSuccessSub:'Sign in to start adding your tasks.',passwordRequired:'Enter your password.',descriptionSearch:'Search by title or description',loadingPreview:'Loading tasks',listErrorPreview:'Task loading error',saveErrorPreview:'Task save error',savingPreview:'Saving a task',successPreview:'Task saved',authErrorPreview:'Incorrect sign-in details',registrationSuccessPreview:'Registration success',backendScope:'Title, description, due date and completion status.',taskCount:'Your tasks',dateFormat:'Day / month / year',selectedState:'Selected',pendingState:'Pending',successState:'Success'});

const seed = [
 {id:1,vi:'Chuẩn bị báo cáo quý 4',en:'Prepare the Q4 report',date:'2026-11-04',time:'16:00',priority:true,notesVi:'Tổng hợp kết quả, các điểm cần lưu ý và kế hoạch cho quý tiếp theo.',notesEn:'Summarize results, key considerations and plans for the next quarter.'},
 {id:2,vi:'Gửi bản tóm tắt cho đội sản phẩm',en:'Send the summary to the product team',date:'2026-11-05',priority:false},
 {id:3,vi:'Chốt lịch phỏng vấn người dùng',en:'Schedule user interviews',date:'2026-11-06',priority:false},
 {id:4,vi:'Rà soát nội dung phát hành',en:'Review the release notes',date:'2026-11-09',priority:false},
 {id:5,vi:'Lên kế hoạch cho đợt làm việc tiếp theo',en:'Plan the next sprint',date:'',priority:false},
 {id:6,vi:'Kiểm tra và gửi hóa đơn tháng 10',en:'Review and send October invoices',date:'2026-11-03',priority:true},
 {id:7,vi:'Cập nhật kế hoạch chi tiêu tháng 11',en:'Update the November spending plan',date:'2026-11-12',priority:false},
 {id:8,vi:'Sắp xếp tài liệu tham khảo cho dự án mới',en:'Organize reference material for the new project',date:'',priority:false},
 {id:9,vi:'Dọn hộp thư tuần này',en:'Clear this week’s inbox',date:'2026-11-03',done:true,completed:'03/11'},
 {id:10,vi:'Cập nhật tài liệu hướng dẫn hội nhập',en:'Update the onboarding guide',date:'2026-11-03',done:true,completed:'03/11'},
 {id:11,vi:'Rà soát thiết kế trang cài đặt',en:'Review the settings page design',date:'2026-11-02',done:true,completed:'02/11'},
 {id:12,vi:'Tổng hợp ghi chú cuộc họp',en:'Consolidate meeting notes',date:'2026-11-02',done:true,completed:'02/11'}
];
const params=new URLSearchParams(location.search);
function preference(key, fallback){try{return localStorage.getItem('task-design-'+key)||fallback}catch{return fallback}}
const state={lang:['vi','en'].includes(params.get('lang'))?params.get('lang'):preference('lang','vi'),theme:params.get('theme')||preference('theme','light'),collapsed:params.get('sidebar')?params.get('sidebar')==='collapsed':preference('sidebar','expanded')==='collapsed',view:location.hash.slice(1)||params.get('view')||'overview',filter:['all','open','done'].includes(params.get('filter'))?params.get('filter'):'all',search:'',page:Math.max(1,Number(params.get('page'))||1),tasks:seed.map(x=>({...x})),empty:false,listState:'ready',authState:'ready'};
const t=key=>dictionary[state.lang][key]||key;
const title=x=>x[state.lang]||x.vi;
const notes=x=>x.notes??(state.lang==='vi'?x.notesVi:x.notesEn)??'';

const sampleDescriptions={
1:['Tổng hợp kết quả và những việc cần hoàn tất trước buổi rà soát cuối quý.','Summarize results and outstanding work for the end-of-quarter review.'],
2:['Tóm tắt các quyết định đã thống nhất và những bước tiếp theo.','Summarize agreed decisions and the next steps.'],
3:['Xác nhận danh sách người tham gia và gửi lời mời phỏng vấn.','Confirm the participants and send interview invitations.'],
4:['Kiểm tra nội dung, đường dẫn và các thay đổi trong phiên bản mới.','Check the copy, links and changes in the new release.'],
5:['Ghi lại mục tiêu, phạm vi và những đầu việc cần chuẩn bị.','Write down goals, scope and the work that needs preparation.'],
6:['Đối chiếu thông tin và gửi các hóa đơn còn lại của tháng.','Check the details and send the remaining monthly invoices.'],
7:['Rà soát các khoản cố định và cập nhật chi phí dự kiến.','Review recurring expenses and update estimated costs.'],
8:['Gom các tài liệu liên quan, loại bỏ bản trùng và đặt tên thống nhất.','Collect relevant material, remove duplicates and use consistent names.'],
9:['Lưu trữ thư đã xử lý và trả lời những thư còn lại.','Archive processed messages and reply to the remaining ones.'],
10:['Cập nhật hướng dẫn để người mới dễ tìm được thông tin cần thiết.','Update the guide so new joiners can find what they need.'],
11:['Kiểm tra tính nhất quán của các lựa chọn và trạng thái hiển thị.','Check the consistency of preferences and display states.'],
12:['Ghi lại các quyết định và công việc cần theo dõi sau cuộc họp.','Record decisions and follow-up work from the meeting.']};
const description=x=>x.description??x.notes??(state.lang==='vi'?x.notesVi:x.notesEn)??sampleDescriptions[x.id]?.[state.lang==='vi'?0:1]??'';

const currentDate='2026-11-04';
const openTasks=()=>state.tasks.filter(x=>!x.done);
const completedTasks=()=>state.tasks.filter(x=>x.done);
const upcomingTasks=()=>openTasks().filter(x=>x.date>=currentDate&&x.date<='2026-11-11').sort((a,b)=>a.date.localeCompare(b.date));
function dueLabel(x,relative=true){if(!x.date)return t('noDate');if(relative){if(x.date===currentDate)return t('today');if(x.date==='2026-11-05')return t('tomorrow');if(x.date==='2026-11-06')return t('friday');if(x.date<currentDate&&!x.done)return t('overdue')+' · '+x.date.slice(8)+'/'+x.date.slice(5,7)}return x.date.slice(8)+'/'+x.date.slice(5,7)}
function setPreference(key,value){try{localStorage.setItem('task-design-'+key,value)}catch{}}
function applyPreferences(){document.documentElement.dataset.theme=state.theme;document.documentElement.lang=state.lang;const skip=$('.skip-link');if(skip)skip.textContent=state.lang==='vi'?'Đến nội dung chính':'Skip to main content';document.body.classList.toggle('rail',state.collapsed)}
function navItem(view,name,glyph,count){return `<button class="nav-item ${state.view===view?'active':''}" data-nav="${view}" ${state.view===view?'aria-current="page"':''} title="${t(name)}">${icon(glyph)}<span class="nav-label">${t(name)}</span>${count!==undefined?`<span class="nav-count">${count}</span>`:''}</button>`}
function headerControls(){return `<div class="top-controls"><button class="top-language" data-action="language" aria-label="${state.lang==='vi'?'Switch to English':'Chuyển sang tiếng Việt'}">${state.lang==='vi'?'VI':'EN'} ${icon('chevron-down')}</button><button class="icon-button" data-action="theme" title="${t(state.theme==='light'?'dark':'light')}" aria-label="${t(state.theme==='light'?'dark':'light')}">${icon(state.theme==='light'?'moon':'sun')}</button><button class="icon-button" data-action="account" aria-label="${t('account')}" title="${t('account')}"><span class="avatar">MA</span></button></div>`}
function heading(view){const sub={overview:'overviewSub',tasks:'tasksSub',completed:'completedSub',settings:'settingsSub',library:'librarySub'};return `<div class="page-heading"><div class="heading-copy"><h1>${t(view)}</h1><p>${t(sub[view])}</p></div>${['overview','tasks'].includes(view)?`<button class="button primary" data-action="create">${icon('plus')}${t('create')}</button>`:view==='settings'?`<span class="badge green">${icon('check')}${t('personal')}</span>`:''}</div>`}
function shell(content){return `<div class="app-shell"><button class="drawer-backdrop" data-action="drawer-close" aria-label="${t('close')}"></button><aside class="sidebar" id="sidebar"><a class="workspace" href="#overview" title="${t('workspace')}"><span class="workspace-mark">${icon('check')}</span><span>${t('workspace')}</span></a><p class="nav-caption">${t('navigation')}</p><nav class="nav-items" aria-label="${t('workspace')}">${navItem('overview','overview','panels-top-left')}${navItem('tasks','tasks','list-todo',openTasks().length)}${navItem('completed','completed','circle-check',completedTasks().length)}</nav><div class="sidebar-bottom"><nav class="nav-items" aria-label="${t('settings')}">${navItem('settings','settings','settings-2')}<button class="nav-item" data-action="collapse" title="${t(state.collapsed?'expand':'collapse')}">${icon('panel-left-close')}<span class="nav-label">${t('collapse')}</span></button></nav><div class="sidebar-foot"><button class="profile" data-action="account" title="${t('account')}"><span class="avatar">MA</span><span class="profile-copy"><span class="profile-name">Minh Anh</span><span class="profile-type">${t('personal')}</span></span>${icon('chevrons-up-down')}</button></div></div></aside><header class="topbar"><div class="row"><button class="icon-button menu-toggle" data-action="drawer" aria-expanded="false" aria-controls="sidebar" aria-label="${t('menu')}">${icon('menu')}</button><div class="breadcrumb"><span class="workspace-crumb">${t('workspace')}</span><span class="crumb-slash">/</span><span class="current">${t(state.view)}</span></div></div>${headerControls()}</header><main class="content" id="main" tabindex="-1">${heading(state.view)}${content}<footer class="page-foot"><span>${t('sample')}</span><button class="text-button" data-nav="library">${icon('component')}${t('library')}</button></footer></main></div>`}
function checkbox(x){return `<button class="check-button" data-complete="${x.id}" aria-pressed="${!!x.done}" aria-label="${t(x.done?'reopenAction':'completeAction')}: ${esc(title(x))}"><span class="check-box">${icon('check')}</span></button>`}
function moreButton(x){return `<button class="icon-button" data-menu="${x.id}" aria-label="${t('taskAction')}: ${esc(title(x))}" aria-haspopup="menu" title="${t('taskAction')}">${icon('ellipsis')}</button>`}
function priorityRow(x){return `<div class="task-row ${x.done?'completed':''}">${checkbox(x)}<div class="task-info"><button class="task-title" data-edit="${x.id}">${esc(title(x))}</button><div class="task-meta"><span class="date-chip ${x.date&&x.date<currentDate?'overdue':''}">${icon(x.date&&x.date<currentDate?'circle-alert':'calendar-days')}${esc(dueLabel(x))}${x.time?' · '+esc(x.time):''}</span></div></div>${x.priority?`<span class="badge ${x.date&&x.date<currentDate?'red':'amber'}">${icon('flag')}${t('high')}</span>`:''}${moreButton(x)}</div>`}
function overview(){const overdue=openTasks().filter(x=>x.date&&x.date<currentDate);const upcoming=upcomingTasks();const next=openTasks().filter(x=>!overdue.includes(x)).sort((a,b)=>(a.date||'z').localeCompare(b.date||'z')).slice(0,4);const today=openTasks().find(x=>x.date===currentDate);const recent=completedTasks().slice(0,2);return `<section class="summary" aria-label="${t('total')}"><div class="metric"><div class="metric-label">${icon('list-todo')}${t('open')}</div><div class="metric-value"><strong>${openTasks().length.toString().padStart(2,'0')}</strong></div><p class="metric-sub">${t('openSub')}</p></div><div class="metric"><div class="metric-label">${icon('calendar-days')}${t('upcoming')}</div><div class="metric-value"><strong>${upcoming.length.toString().padStart(2,'0')}</strong></div><p class="metric-sub">${t('upcomingSub')}</p></div><div class="metric"><div class="metric-label">${icon('circle-check')}${t('done')}</div><div class="metric-value"><strong>${completedTasks().length.toString().padStart(2,'0')}</strong></div><p class="metric-sub">${t('doneSub')}</p></div></section><div class="dashboard-grid"><section class="panel"><div class="panel-heading"><h2>${t('priorities')}<span class="tiny-count">${overdue.length+next.length}</span></h2><button class="text-button" data-nav="tasks">${t('allTasks')}${icon('arrow-up-right')}</button></div>${overdue.length?`<div class="priority-label"><span class="eyebrow">${t('attention')}</span><span class="badge red">${overdue.length} ${t('overdue').toLowerCase()}</span></div>${overdue.map(priorityRow).join('')}<div class="task-group-divider"></div>`:''}<div class="priority-label"><span class="eyebrow">${t('next')}</span></div>${next.map(priorityRow).join('')}${!overdue.length&&!next.length?emptyMarkup('emptyTitle','emptySub','create'):''}<div class="panel-bottom">${icon('circle-check')}<span>${state.lang==='vi'?'Đánh dấu để hoàn thành. Bạn luôn có thể mở lại.':'Check a task to finish it. You can always reopen it.'}</span></div></section><aside class="aside-stack"><section class="today-panel"><div class="date-line"><span>${t('today')} · ${state.lang==='vi'?'Thứ tư':'Wednesday'}</span><span class="calendar-date">04</span></div><h2>${t(today?'smallSteps':'todayClear')}</h2><p>${t(today?'todayMessage':'todayClearMessage')}</p>${today?`<div class="today-task row between"><div><strong>${esc(title(today))}</strong><p class="row">${icon('clock-3')}${today.time||t('noTime')}</p></div><button class="icon-button border" data-edit="${today.id}" title="${t('viewTask')}" aria-label="${t('viewTask')}">${icon('arrow-up-right')}</button></div>`:''}</section><section class="panel"><div class="panel-heading"><h2>${t('week')}</h2>${icon('calendar-days')}</div><div class="deadline-list">${upcoming.filter(x=>x!==today).slice(0,3).map(x=>`<div class="deadline"><span class="deadline-date"><span>${state.lang==='vi'?'TH 11':'NOV'}</span><strong>${x.date.slice(8)}</strong></span><div class="deadline-copy"><button class="task-title" data-edit="${x.id}">${esc(title(x))}</button><p>${dueLabel(x)} · ${x.time||t('noTime')}</p></div></div>`).join('')||`<p class="small muted" style="padding:var(--space-4) 0">${t('noUpcomingSub')}</p>`}</div></section></aside></div><section class="panel recent"><div class="panel-heading"><h2>${t('recent')}</h2><button class="text-button" data-nav="completed">${t('viewCompleted')}${icon('arrow-up-right')}</button></div><div class="recent-list">${recent.map(x=>`<div class="recent-item">${icon('circle-check')}<div><button class="task-title" data-edit="${x.id}">${esc(title(x))}</button><p>${t('recentDate')} ${x.completed||'04/11'}</p></div></div>`).join('')||`<p class="small muted">${t('emptyCompleted')}</p>`}</div></section>`}
function emptyMarkup(headingKey,bodyKey,action){return `<div class="empty-state"><span class="empty-symbol">${icon(action==='clear'?'search-x':'list-check')}</span><h2>${t(headingKey)}</h2><p>${t(bodyKey)}</p>${action?`<button class="button ${action==='create'?'primary':''}" data-action="${action}">${icon(action==='create'?'plus':'rotate-ccw')}${t(action==='create'?'create':'clearSearch')}</button>`:''}</div>`}
function render(){applyPreferences();document.body.classList.remove('drawer-open');const auth=['login','register','loggedout'].includes(state.view);document.title=t(auth?state.view==='loggedout'?'signout':state.view==='login'?'signin':'register':state.view)+' · '+t('workspace');$('#app').innerHTML=auth?authScreen():shell(state.view==='overview'?overview():state.view==='tasks'||state.view==='completed'?taskScreen():state.view==='settings'?settingsScreen():libraryScreen());bind();}
function navigate(view){state.view=['overview','tasks','completed','settings','library','login','register','loggedout'].includes(view)?view:'overview';state.search='';state.page=1;state.empty=false;state.listState='ready';state.authState='ready';closeMenu();history.replaceState(null,'','#'+state.view);render();window.scrollTo({top:0,behavior:'instant'})}
function bind(){document.querySelectorAll('[data-nav]').forEach(b=>b.onclick=()=>navigate(b.dataset.nav));document.querySelectorAll('[data-complete]').forEach(b=>b.onclick=()=>{const x=state.tasks.find(x=>x.id===+b.dataset.complete);x.done=!x.done;x.completed='04/11';render();toast(t(x.done?'markedDone':'markedOpen'))});document.querySelectorAll('[data-edit]').forEach(b=>b.onclick=()=>taskDialog(+b.dataset.edit));document.querySelectorAll('[data-menu]').forEach(b=>b.onclick=e=>{e.stopPropagation();taskMenu(+b.dataset.menu,b)});document.querySelectorAll('[data-action]').forEach(b=>b.onclick=e=>action(b.dataset.action,b,e));bindScreen();}
function action(name,button,event){if(name==='create')taskDialog();if(name==='retry-list'){state.listState='ready';render()}if(name==='theme'){state.theme=state.theme==='light'?'dark':'light';setPreference('theme',state.theme);render()}if(name==='language'){state.lang=state.lang==='vi'?'en':'vi';setPreference('lang',state.lang);render()}if(name==='collapse'){state.collapsed=!state.collapsed;setPreference('sidebar',state.collapsed?'collapsed':'expanded');render()}if(name==='drawer'){document.body.classList.add('drawer-open');$('.sidebar').setAttribute('role','dialog');$('.sidebar').setAttribute('aria-modal','true');$('.sidebar').setAttribute('aria-label',t('workspace'));button.setAttribute('aria-expanded','true');$('.sidebar .nav-item').focus()}if(name==='drawer-close')closeDrawer();if(name==='account'){event?.stopPropagation();accountMenu(button)}if(name==='clear'){state.search='';state.empty=false;state.page=1;render()}if(name==='reset'){state.tasks=seed.map(x=>({...x}));state.empty=false;render();toast(t('resetDemo'))}}
function closeDrawer(){document.body.classList.remove('drawer-open');$('.sidebar')?.removeAttribute('role');$('.sidebar')?.removeAttribute('aria-modal');const b=$('[data-action="drawer"]');b?.setAttribute('aria-expanded','false');b?.focus()}
function toast(message,persistent=false){$('#toast')?.remove();const el=document.createElement('div');el.id='toast';el.className='toast';el.role='status';el.innerHTML=icon('circle-check')+esc(message);document.body.append(el);if(!persistent)setTimeout(()=>el.remove(),3200)}
function closeMenu(){$('#context-menu')?.remove()}
function positionMenu(button,markup){closeMenu();const menu=document.createElement('div');menu.id='context-menu';menu.className='dropdown';menu.role='menu';menu.innerHTML=markup;document.body.append(menu);const r=button.getBoundingClientRect();menu.style.left=Math.max(8,Math.min(r.right-menu.offsetWidth,innerWidth-menu.offsetWidth-8))+'px';menu.style.top=Math.max(8,Math.min(r.bottom+4,innerHeight-menu.offsetHeight-8))+'px';menu.querySelector('button')?.focus();menu.addEventListener('keydown',e=>{const items=[...menu.querySelectorAll('button')];let n=items.indexOf(document.activeElement);if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();items[(n+(e.key==='ArrowDown'?1:-1)+items.length)%items.length].focus()}});return menu}
function taskMenu(id,button){const x=state.tasks.find(x=>x.id===id);const menu=positionMenu(button,`<button role="menuitem" data-edit-action>${icon('pencil')}${t('edit')}</button><button role="menuitem" data-complete-action>${icon(x.done?'rotate-ccw':'circle-check')}${t(x.done?'reopenAction':'completeAction')}</button><div class="divider" style="margin:var(--space-1) 0"></div><button role="menuitem" class="destructive" data-delete-action>${icon('trash')}${t('delete')}</button>`);$('[data-edit-action]',menu).onclick=()=>{closeMenu();taskDialog(id)};$('[data-complete-action]',menu).onclick=()=>{x.done=!x.done;closeMenu();render();toast(t(x.done?'markedDone':'markedOpen'))};$('[data-delete-action]',menu).onclick=()=>{closeMenu();deleteDialog(id)}}
function accountMenu(button){const menu=positionMenu(button,`<button role="menuitem" data-settings-action>${icon('settings-2')}${t('settings')}</button><button role="menuitem" data-logout-action>${icon('log-out')}${t('signout')}</button>`);$('[data-settings-action]',menu).onclick=()=>navigate('settings');$('[data-logout-action]',menu).onclick=()=>navigate('loggedout')}
document.addEventListener('click',e=>{if(!e.target.closest('#context-menu'))closeMenu()});document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeMenu();if(document.body.classList.contains('drawer-open'))closeDrawer()}});window.addEventListener('hashchange',()=>{const route=location.hash.slice(1);if(['overview','tasks','completed','settings','library','login','register','loggedout'].includes(route))navigate(route)});
document.addEventListener('keydown',e=>{if(e.key==='Tab'&&document.body.classList.contains('drawer-open')){const items=[...document.querySelectorAll('.sidebar a,.sidebar button')];const first=items[0],last=items[items.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}});
function statusBadge(x){return `<span class="badge ${x.done?'green':''}">${icon(x.done?'circle-check':'circle-dashed')}${t(x.done?'finished':'open')}</span>`}
function taskScreen(){const counts={all:state.tasks.length,open:openTasks().length,done:completedTasks().length};return `<section class="panel task-panel" aria-label="${t('tasks')}"><div class="toolbar">${state.view==='tasks'?`<div class="tabs" role="tablist" aria-label="${t('status')}">${[['all','all'],['open','incomplete'],['done','finished']].map(([key,label])=>`<button class="tab ${state.filter===key?'active':''}" role="tab" aria-selected="${state.filter===key}" tabindex="${state.filter===key?'0':'-1'}" data-filter="${key}" aria-controls="task-results">${t(label)}<span class="tab-count">${counts[key]}</span></button>`).join('')}</div>`:`<span class="small muted">${counts.done} ${t('taskUnit')}</span>`}<label class="search-wrap">${icon('search')}<span class="sr-only">${t('descriptionSearch')}</span><input id="task-search" type="search" autocomplete="off" placeholder="${t('search')}" value="${esc(state.search)}"></label></div><div class="table-head" aria-hidden="true"><span>${t('task')}</span><span>${t('status')}</span><span>${t('due')}</span><span></span></div><div id="task-results" role="region" aria-label="${t('tasks')}" aria-live="polite" aria-busy="${state.listState==='loading'}">${taskResults()}</div></section>`}
function filteredTasks(){const query=state.search.toLocaleLowerCase(state.lang);return state.empty?[]:state.tasks.filter(x=>(state.view==='completed'?x.done:state.filter==='open'?!x.done:state.filter==='done'?x.done:true)&&(title(x)+' '+description(x)).toLocaleLowerCase(state.lang).includes(query))}
function taskResults(){
 if(state.listState==='loading')return loadingMarkup();
 if(state.listState==='error')return `<div class="empty-state error-state"><span class="empty-symbol">${icon('circle-alert')}</span><h2>${t('loadError')}</h2><p>${t('loadErrorSub')}</p><button class="button" data-action="retry-list">${icon('rotate-ccw')}${t('retry')}</button></div>`;
 const filtered=filteredTasks();if(!filtered.length)return state.search?emptyMarkup('noResults','noResultsSub','clear'):state.view==='completed'||state.filter==='done'?emptyMarkup('emptyCompleted','emptyCompletedSub'):emptyMarkup('emptyTitle','emptySub','create');
 const pageSize=7,pages=Math.ceil(filtered.length/pageSize);state.page=Math.min(state.page,pages);const rows=filtered.slice((state.page-1)*pageSize,state.page*pageSize);
 return rows.map(x=>`<article class="list-row ${x.done?'completed':''}" aria-label="${esc(title(x))}"><div class="list-task">${checkbox(x)}<div class="list-task-copy"><button class="task-title" data-edit="${x.id}">${esc(title(x))}</button><p class="description-preview" title="${esc(description(x))}">${esc(description(x)||t('descriptionEmpty'))}</p></div></div>${statusBadge(x)}<span class="list-date ${x.date&&x.date<currentDate&&!x.done?'overdue':''}">${x.date?icon('calendar-days'):icon('minus')}<span>${esc(dueLabel(x,false))}${x.date&&x.date<currentDate&&!x.done?`<small>${t('overdue')}</small>`:''}</span></span>${moreButton(x)}</article>`).join('')+`<div class="list-footer"><span>${t('showing')} ${(state.page-1)*pageSize+1}–${Math.min(state.page*pageSize,filtered.length)} ${t('of')} ${filtered.length} ${t('taskUnit')}</span><nav class="pagination" aria-label="${t('page')}"><button class="icon-button border" data-page="${state.page-1}" ${state.page===1?'disabled':''} aria-label="${t('previousPage')}">${icon('chevron-left')}</button>${Array.from({length:pages},(_,i)=>`<button class="page-number ${state.page===i+1?'current':''}" data-page="${i+1}" ${state.page===i+1?'aria-current="page"':''}>${i+1}</button>`).join('')}<button class="icon-button border" data-page="${state.page+1}" ${state.page===pages?'disabled':''} aria-label="${t('nextPage')}">${icon('chevron-right')}</button></nav></div>`;
}
function loadingMarkup(){return `<div class="loading-label" role="status">${icon('clock-3')}${t('loading')}</div><div class="loading-rows" aria-hidden="true">${Array.from({length:5},()=>`<div class="loading-row"><span class="skeleton-check"></span><div><span class="skeleton-line"></span><span class="skeleton-line short"></span></div><span class="skeleton-status"></span></div>`).join('')}</div>`}

function choice(group,value,label,description,glyph,checked){return `<button class="choice" role="radio" aria-checked="${checked}" data-preference="${group}" data-value="${value}"><span class="choice-icon">${icon(glyph)}</span><span class="choice-copy"><strong>${t(label)}</strong><small>${t(description)}</small></span><span class="radio-dot">${icon('check')}</span></button>`}
function settingsScreen(){return `<div class="settings-grid"><div class="settings-stack"><section class="panel setting-panel"><h2 id="language-title">${t('language')}</h2><p>${t('languageSub')}</p><div role="radiogroup" aria-labelledby="language-title">${choice('lang','vi','vietnamese','langViDesc','languages',state.lang==='vi')}${choice('lang','en','english','langEnDesc','languages',state.lang==='en')}</div></section><section class="panel setting-panel"><h2 id="appearance-title">${t('appearance')}</h2><p>${t('appearanceSub')}</p><div role="radiogroup" aria-labelledby="appearance-title">${choice('theme','light','light','lightSub','sun',state.theme==='light')}${choice('theme','dark','dark','darkSub','moon',state.theme==='dark')}</div></section><section class="panel setting-panel"><h2 id="sidebar-title">${t('sidebar')}</h2><p>${t('sidebarSub')}</p><div role="radiogroup" aria-labelledby="sidebar-title">${choice('sidebar','expanded','expanded','expandedSub','panel-left',!state.collapsed)}${choice('sidebar','collapsed','collapsed','collapsedSub','panel-left-close',state.collapsed)}</div></section><div class="saved-note">${icon('circle-check')}${t('autoSaved')}</div></div><aside class="panel setting-panel account-card"><div class="row"><span class="avatar">MA</span><div><h2>Minh Anh</h2><p class="small muted">${t('personal')}</p></div></div><div class="divider"></div><h3>${t('account')}</h3><dl><div><dt>${t('displayName')}</dt><dd>Minh Anh</dd></div><div><dt>${t('username')}</dt><dd>minhanh</dd></div><div><dt>${t('email')}</dt><dd>minhanh@example.com</dd></div><div><dt>${t('currentLanguage')}</dt><dd>${t(state.lang==='vi'?'vietnamese':'english')}</dd></div></dl><div class="divider"></div><button class="text-button" data-nav="loggedout">${icon('log-out')}${t('signout')}</button></aside></div>`}
function bindScreen(){
 document.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>{state.filter=b.dataset.filter;state.page=1;state.empty=false;render()});
 const search=$('#task-search');if(search)search.oninput=()=>{state.search=search.value;state.page=1;$('#task-results').innerHTML=taskResults();bindResults()};
 bindResults();
 document.querySelectorAll('[data-preference]').forEach(b=>b.onclick=()=>{const group=b.dataset.preference,value=b.dataset.value;if(group==='sidebar')state.collapsed=value==='collapsed';else state[group]=value;setPreference(group,value);render();toast(t('savedPreference'));$(`[data-preference="${group}"][data-value="${value}"]`)?.focus()});
 document.querySelectorAll('[role="radiogroup"]').forEach(group=>group.onkeydown=e=>{if(['ArrowDown','ArrowRight','ArrowUp','ArrowLeft'].includes(e.key)){e.preventDefault();const items=[...group.querySelectorAll('[role="radio"]')];const next=(items.indexOf(document.activeElement)+(e.key==='ArrowDown'||e.key==='ArrowRight'?1:-1)+items.length)%items.length;items[next].click()}});
 document.querySelectorAll('[data-filter]').forEach(b=>b.onkeydown=e=>{if(['ArrowRight','ArrowLeft'].includes(e.key)){e.preventDefault();const items=[...document.querySelectorAll('[data-filter]')];const key=items[(items.indexOf(b)+(e.key==='ArrowRight'?1:-1)+items.length)%items.length].dataset.filter;state.filter=key;state.page=1;render();$(`[data-filter="${key}"]`)?.focus()}});
 document.querySelectorAll('[data-preview]').forEach(b=>b.onclick=()=>preview(b.dataset.preview));
 const form=$('#auth-form');if(form)form.onsubmit=submitAuth;
 document.querySelectorAll('[data-password]').forEach(b=>b.onclick=()=>{const input=$('#'+b.dataset.password);input.type=input.type==='password'?'text':'password';b.innerHTML=icon(input.type==='password'?'eye':'eye-off');b.setAttribute('aria-label',t(input.type==='password'?'showPassword':'hidePassword'))});
}
function bindResults(){const results=$('#task-results');if(!results)return;results.querySelectorAll('[data-complete]').forEach(b=>b.onclick=()=>{const x=state.tasks.find(x=>x.id===+b.dataset.complete);x.done=!x.done;x.completed='04/11';render();toast(t(x.done?'markedDone':'markedOpen'))});results.querySelectorAll('[data-edit]').forEach(b=>b.onclick=()=>taskDialog(+b.dataset.edit));results.querySelectorAll('[data-menu]').forEach(b=>b.onclick=e=>{e.stopPropagation();taskMenu(+b.dataset.menu,b)});results.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>{state.page=+b.dataset.page;$('#task-results').innerHTML=taskResults();bindResults()});results.querySelectorAll('[data-action]').forEach(b=>b.onclick=e=>action(b.dataset.action,b,e))}
let returnFocus=null;
function openDialog(markup,setup){document.querySelector('dialog')?.remove();returnFocus=document.activeElement;const dialog=document.createElement('dialog');dialog.setAttribute('aria-labelledby','dialog-title');dialog.innerHTML=markup;document.body.append(dialog);dialog.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}});dialog.addEventListener('close',()=>{dialog.remove();if(returnFocus?.isConnected)returnFocus.focus()});setup?.(dialog);dialog.showModal();return dialog}
function taskDialog(id,invalid=false,mode='ready'){
 const x=state.tasks.find(x=>x.id===id),busy=mode==='saving',failed=mode==='error';
 return openDialog(`<form id="task-form" novalidate aria-busy="${busy}"><div class="dialog-header"><div><h2 id="dialog-title">${t(x?'editTitle':'createTitle')}</h2><p class="dialog-intro">${t('formIntro')}</p></div><button type="button" class="icon-button" data-close aria-label="${t('close')}">${icon('x')}</button></div><div class="dialog-body"><div class="feedback error" id="task-save-error" role="alert" ${failed?'':'hidden'}>${icon('circle-alert')}<span>${t('saveError')}</span></div><div class="field"><label for="task-name">${t('taskName')} <span class="required-mark" aria-hidden="true">*</span></label><input class="input" id="task-name" name="title" value="${x?esc(title(x)):''}" placeholder="${t('namePlaceholder')}" required aria-describedby="name-hint name-error" ${invalid?'aria-invalid="true"':''} autofocus><p class="field-hint" id="name-hint">${t('nameHint')}</p><p id="name-error" class="field-error" ${invalid?'':'hidden'}>${icon('circle-alert')}${t('nameError')}</p></div><div class="field"><label for="task-description">${t('description')} <span class="optional-label">(${t('optional')})</span></label><textarea class="textarea task-description" id="task-description" name="description" aria-describedby="description-hint" placeholder="${t('descriptionPlaceholder')}">${x?esc(description(x)):''}</textarea><p class="field-hint" id="description-hint">${t('descriptionHint')}</p></div><div class="field"><label for="task-date">${t('due')} <span class="optional-label">(${t('optional')})</span></label><input class="input" type="date" id="task-date" name="due_date" value="${x?.date||''}" aria-describedby="due-hint"><p class="field-hint" id="due-hint">${t('dueHelp')}</p></div><div class="completion-field"><label for="task-done"><input id="task-done" name="completed" type="checkbox" ${x?.done?'checked':''}><span><strong>${t('done')}</strong><small>${t('completionHelp')}</small></span></label></div>${busy?`<div class="saving-note" role="status">${icon('clock-3')}${t('savingHelp')}</div>`:''}</div><div class="dialog-footer"><span class="shortcut">Esc · ${t('cancel')}</span><button type="button" class="button" data-close>${t('cancel')}</button><button type="submit" class="button primary" ${busy?'disabled':''}>${icon(busy?'clock-3':x?'check':'plus')}${t(busy?'saving':x?'save':'create')}</button></div></form>`,dialog=>{
 const form=$('#task-form',dialog),name=$('#task-name',dialog);
 form.onsubmit=e=>{e.preventDefault();if(busy)return;const valid=!!name.value.trim();$('#name-error',dialog).hidden=valid;name.setAttribute('aria-invalid',String(!valid));if(!valid){name.focus();return}
 const values={date:$('#task-date',dialog).value,description:$('#task-description',dialog).value,done:$('#task-done',dialog).checked};if(values.done)values.completed='04/11';
 if(x){Object.assign(x,values,{[state.lang]:name.value.trim()});if(x.userCreated)x.vi=x.en=name.value.trim()}else state.tasks.unshift({id:Date.now(),vi:name.value.trim(),en:name.value.trim(),userCreated:true,...values});
 state.empty=false;state.listState='ready';state.page=1;if(!x){state.search='';if(state.view==='completed'){state.view='tasks';history.replaceState(null,'','#tasks')}state.filter='all'}dialog.close();render();$('[data-action="create"]')?.focus();toast(t(x?'updated':'created'))};
 name.oninput=()=>{name.removeAttribute('aria-invalid');$('#name-error',dialog).hidden=true};
 });
}

function deleteDialog(id){const x=state.tasks.find(x=>x.id===id);if(!x)return;openDialog(`<div class="dialog-header"><h2 id="dialog-title">${t('deleteTitle')}</h2><button class="icon-button" data-close aria-label="${t('close')}">${icon('x')}</button></div><div class="dialog-body"><span class="delete-symbol">${icon('trash')}</span><p class="delete-copy"><strong>${esc(title(x))}</strong></p><p class="delete-copy">${t('deleteWarning')}</p></div><div class="dialog-footer"><button class="button" data-close autofocus>${t('keepTask')}</button><button class="button danger" id="confirm-delete">${icon('trash')}${t('delete')}</button></div>`,dialog=>{$('#confirm-delete',dialog).onclick=()=>{state.tasks=state.tasks.filter(task=>task.id!==id);dialog.close();render();toast(t('deleted'))}})}
function authScreen(){
 const logout=state.view==='loggedout',register=state.view==='register',busy=state.authState==='loading',error=state.authState==='error',success=state.authState==='success';
 return `<div class="auth-page"><header class="auth-topbar"><a class="auth-brand" href="#overview"><span class="workspace-mark">${icon('check')}</span>${t('workspace')}</a><div class="top-controls"><button class="top-language" data-action="language" aria-label="${t('language')}">${state.lang==='vi'?'VI':'EN'} ${icon('chevron-down')}</button><button class="icon-button" data-action="theme" aria-label="${t(state.theme==='light'?'dark':'light')}">${icon(state.theme==='light'?'moon':'sun')}</button></div></header><main class="auth-main" id="main"><section class="auth-card auth-surface">${logout?`<span class="auth-status-mark">${icon('log-out')}</span><h1>${t('logoutHeading')}</h1><p class="muted">${t('logoutSub')}</p><button class="button primary" data-nav="login">${t('signin')}${icon('arrow-right')}</button><p class="auth-switch">${t('logoutNotice')}</p>`:success?`<span class="auth-status-mark success">${icon('circle-check')}</span><h1>${t('registerSuccess')}</h1><p class="muted">${t('registerSuccessSub')}</p><button class="button primary" data-nav="login">${t('signin')}${icon('arrow-right')}</button>`:`<div class="auth-heading"><span class="auth-status-mark">${icon(register?'list-check':'arrow-right-to-line')}</span><h1>${t(register?'register':'signin')}</h1><p>${t(register?'registerSub':'loginSub')}</p></div><form id="auth-form" novalidate aria-busy="${busy}"><div id="auth-server-error" class="feedback error" role="alert" ${error?'':'hidden'}>${icon('circle-alert')}<span>${t(register?'registrationError':'loginError')}</span></div><p id="auth-error" class="field-error" role="alert" hidden>${t('authError')}</p><div class="field"><label for="auth-name">${t('username')}</label><input class="input" id="auth-name" name="username" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="${t('usernamePlaceholder')}" value="${error||busy?'minhanh':''}" required aria-describedby="auth-name-error" ${busy?'disabled':''}><p class="field-error" id="auth-name-error" hidden>${t('usernameError')}</p></div>${register?`<div class="field"><label for="auth-email">${t('email')}</label><input class="input" id="auth-email" type="email" name="email" autocomplete="email" placeholder="${state.lang==='vi'?'ban':'you'}@example.com" required aria-describedby="auth-email-error" ${busy?'disabled':''}><p class="field-error" id="auth-email-error" hidden>${t('emailError')}</p></div>`:''}<div class="field"><label for="auth-password">${t('password')}</label><div class="password-field"><input class="input" id="auth-password" type="password" name="password" autocomplete="${register?'new-password':'current-password'}" ${register?'minlength="8"':''} required aria-describedby="auth-password-hint auth-password-error" ${busy?'disabled':''}><button type="button" class="icon-button" data-password="auth-password" aria-label="${t('showPassword')}" ${busy?'disabled':''}>${icon('eye')}</button></div>${register?`<p class="field-hint" id="auth-password-hint">${t('passwordHint')}</p>`:'<span id="auth-password-hint" hidden></span>'}<p class="field-error" id="auth-password-error" hidden>${t(register?'passwordError':'passwordRequired')}</p></div>${register?`<div class="field"><label for="auth-confirm">${t('confirmPassword')}</label><div class="password-field"><input class="input" id="auth-confirm" type="password" name="password_confirm" autocomplete="new-password" required aria-describedby="auth-confirm-error" ${busy?'disabled':''}><button type="button" class="icon-button" data-password="auth-confirm" aria-label="${t('showPassword')}" ${busy?'disabled':''}>${icon('eye')}</button></div><p class="field-error" id="auth-confirm-error" hidden>${t('confirmError')}</p></div>`:''}<button class="button primary" type="submit" ${busy?'disabled':''}>${busy?icon('clock-3'):''}${t(busy?register?'registerLoading':'authLoading':register?'register':'signin')}${busy?'':icon('arrow-right')}</button></form><p class="auth-switch">${t(register?'hasAccount':'noAccount')} <button class="text-button" data-nav="${register?'login':'register'}">${t(register?'signin':'register')}</button></p>`}</section></main><footer class="auth-footer"><p>${t('sample')}</p><button class="text-button" data-nav="overview">${t('demoContinue')}${icon('arrow-up-right')}</button><p class="auth-preview-note">${t('demoNotice')}</p></footer></div>`;
}
function submitAuth(e){
 e.preventDefault();if(state.authState==='loading')return;const form=e.currentTarget,register=state.view==='register';let firstInvalid=null;
 const validate=(id,valid)=>{const input=$('#auth-'+id,form),error=$('#auth-'+id+'-error',form);if(!input)return;input.setAttribute('aria-invalid',String(!valid));error.hidden=valid;if(!valid&&!firstInvalid)firstInvalid=input};
 validate('name',!!$('#auth-name',form).value.trim());if(register)validate('email',$('#auth-email',form).validity.valid&&!!$('#auth-email',form).value.trim());validate('password',register?$('#auth-password',form).value.length>=8:!!$('#auth-password',form).value);if(register)validate('confirm',$('#auth-confirm',form).value===$('#auth-password',form).value&&!!$('#auth-confirm',form).value);
 $('#auth-error',form).hidden=!firstInvalid;if(firstInvalid){firstInvalid.focus();return}
 if(register){state.authState='success';render()}else{$('#auth-server-error',form).hidden=false;$('#auth-password',form).value='';$('#auth-password',form).focus()}
}

const screenDirectory=[
 {
  "id": "TSK-01",
  "group": "taskScreens",
  "label": "allTasksLabel",
  "view": "tasks"
 },
 {
  "id": "TSK-02",
  "group": "taskScreens",
  "label": "incomplete",
  "view": "tasks",
  "filter": "open"
 },
 {
  "id": "TSK-03",
  "group": "taskScreens",
  "label": "completed",
  "view": "completed"
 },
 {
  "id": "TSK-04",
  "group": "taskScreens",
  "label": "emptyPreview",
  "view": "tasks",
  "fixture": "empty"
 },
 {
  "id": "TSK-05",
  "group": "taskScreens",
  "label": "noResults",
  "view": "tasks",
  "fixture": "no-results"
 },
 {
  "id": "TSK-06",
  "group": "taskScreens",
  "label": "emptyCompleted",
  "view": "completed",
  "fixture": "completed-empty"
 },
 {
  "id": "TSK-07",
  "group": "taskScreens",
  "label": "loadingPreview",
  "view": "tasks",
  "fixture": "loading"
 },
 {
  "id": "TSK-08",
  "group": "taskScreens",
  "label": "listErrorPreview",
  "view": "tasks",
  "fixture": "list-error"
 },
 {
  "id": "TSK-09",
  "group": "taskScreens",
  "label": "nextPage",
  "view": "tasks",
  "page": 2
 },
 {
  "id": "FRM-01",
  "group": "formScreens",
  "label": "createTitle",
  "view": "tasks",
  "fixture": "create"
 },
 {
  "id": "FRM-02",
  "group": "formScreens",
  "label": "editTitle",
  "view": "tasks",
  "fixture": "edit"
 },
 {
  "id": "FRM-03",
  "group": "formScreens",
  "label": "deletePreview",
  "view": "tasks",
  "fixture": "delete"
 },
 {
  "id": "FRM-04",
  "group": "formScreens",
  "label": "errorPreview",
  "view": "tasks",
  "fixture": "invalid"
 },
 {
  "id": "FRM-05",
  "group": "formScreens",
  "label": "saveErrorPreview",
  "view": "tasks",
  "fixture": "save-error"
 },
 {
  "id": "FRM-06",
  "group": "formScreens",
  "label": "savingPreview",
  "view": "tasks",
  "fixture": "saving"
 },
 {
  "id": "FRM-07",
  "group": "formScreens",
  "label": "successPreview",
  "view": "tasks",
  "fixture": "success"
 },
 {
  "id": "AUTH-01",
  "group": "accessScreens",
  "label": "signin",
  "view": "login"
 },
 {
  "id": "AUTH-02",
  "group": "accessScreens",
  "label": "register",
  "view": "register"
 },
 {
  "id": "AUTH-03",
  "group": "accessScreens",
  "label": "signout",
  "view": "loggedout"
 },
 {
  "id": "AUTH-04",
  "group": "accessScreens",
  "label": "errorPreview",
  "view": "register",
  "fixture": "auth-invalid"
 },
 {
  "id": "AUTH-05",
  "group": "accessScreens",
  "label": "authErrorPreview",
  "view": "login",
  "fixture": "auth-error"
 },
 {
  "id": "AUTH-06",
  "group": "accessScreens",
  "label": "registrationSuccessPreview",
  "view": "register",
  "fixture": "registered"
 },
 {
  "id": "AUTH-07",
  "group": "accessScreens",
  "label": "authLoading",
  "view": "login",
  "fixture": "auth-loading"
 },
 {
  "id": "AUTH-08",
  "group": "accessScreens",
  "label": "registrationError",
  "view": "register",
  "fixture": "auth-error"
 },
 {
  "id": "SET-01",
  "group": "preferenceScreens",
  "label": "settings",
  "view": "settings"
 },
 {
  "id": "DS-01",
  "group": "preferenceScreens",
  "label": "library",
  "view": "library"
 }
];
function screenHref(screen){const p=new URLSearchParams({view:screen.view,lang:state.lang,theme:state.theme,sidebar:state.collapsed?'collapsed':'expanded'});if(screen.fixture)p.set('state',screen.fixture);if(screen.filter)p.set('filter',screen.filter);if(screen.page)p.set('page',screen.page);return 'index.html?'+p.toString()}
function screenDirectoryMarkup(){return `<section class="panel library-panel wide screen-directory"><h2>${t('screenDirectory')}</h2><p class="directory-intro">${t('screenDirectorySub')}</p>${['taskScreens','formScreens','accessScreens','preferenceScreens'].map(group=>`<div class="screen-group"><h3>${t(group)}</h3><div class="screen-links">${screenDirectory.filter(s=>s.group===group).map(s=>`<a class="screen-link" href="${screenHref(s)}"><span class="screen-code">${s.id}</span><span>${t(s.label)}</span>${icon('arrow-up-right')}</a>`).join('')}</div></div>`).join('')}</section>`}

function libraryScreen(){return `<div class="library-grid">${screenDirectoryMarkup()}<section class="panel library-panel"><h2>${t('colorSystem')}</h2><div class="swatches">${[['--color-bg',state.lang==='vi'?'Nền':'Canvas'],['--color-surface',state.lang==='vi'?'Bề mặt':'Surface'],['--color-text',state.lang==='vi'?'Văn bản':'Text'],['--color-accent',state.lang==='vi'?'Điểm nhấn':'Accent'],['--color-danger',state.lang==='vi'?'Cảnh báo':'Danger']].map(([color,label])=>`<div class="swatch"><span style="background:var(${color})"></span>${label}</div>`).join('')}</div><div class="divider"></div><div class="component-row"><span class="badge green">${icon('circle-check')}${t('finished')}</span><span class="badge">${icon('circle-dashed')}${t('open')}</span><span class="badge red">${icon('circle-alert')}${t('overdue')}</span></div></section><section class="panel library-panel"><h2>${t('typography')}</h2><p class="type-specimen">${state.lang==='vi'?'Tập trung vào việc quan trọng.':'Focus on what matters.'}</p><h2>${state.lang==='vi'?'Một danh sách, một ngày nhẹ hơn.':'One list. A little more room.'}</h2><p class="small muted" style="margin-top:var(--space-4)">Inter · 12 / 13 / 15 / 19 / 23 / 29 px</p><p class="small muted">${state.lang==='vi'?'Khoảng cách':'Spacing'} · 4 / 8 / 12 / 16 / 24 / 32 / 48 px</p></section><section class="panel library-panel wide"><h2>${t('controls')}</h2><div class="component-row"><button class="button primary" data-action="create">${icon('plus')}${t('create')}</button><button class="button">${t('defaultState')}</button><button class="button state-hover">${t('hoverState')}</button><button class="button state-focus">${t('focusState')}</button><button class="button" disabled>${t('disabledState')}</button></div><p class="small muted">${state.lang==='vi'?'Điều khiển có vùng chạm tối thiểu 44 px. Biểu tượng Lucide nét 1,7 px.':'Controls use 44 px minimum hit areas. Lucide icons use 1.7 px strokes.'}</p></section><section class="panel library-panel"><h2>${t('formStates')}</h2><div class="field"><label for="sample-input">${t('taskName')}</label><input id="sample-input" class="input" value="${state.lang==='vi'?'Chuẩn bị báo cáo quý 4':'Prepare the Q4 report'}"></div><div class="field" style="margin-top:var(--space-4)"><label for="sample-error">${t('taskName')}</label><input id="sample-error" class="input" aria-invalid="true" aria-describedby="sample-error-copy"><span class="field-error" id="sample-error-copy">${icon('circle-alert')}${t('nameError')}</span></div></section><section class="panel library-panel"><h2>${t('screenStates')}</h2><div class="library-links"><button class="button" data-action="create">${t('createTitle')}</button><button class="button" data-preview="edit">${t('editTitle')}</button><button class="button" data-preview="delete">${t('deletePreview')}</button><button class="button" data-preview="error">${t('errorPreview')}</button><button class="button" data-preview="empty">${t('emptyPreview')}</button><button class="button" data-nav="login">${t('signin')}</button><button class="button" data-nav="register">${t('register')}</button><button class="button" data-nav="loggedout">${t('signout')}</button></div></section><section class="panel library-panel wide"><h2>${t('successFeedback')} / ${t('errorFeedback')}</h2><div class="feedback-pair"><div class="feedback success">${icon('circle-check')}<span>${t('saved')}</span></div><div class="feedback error">${icon('circle-alert')}<span>${t('saveError')}</span></div></div></section><section class="panel library-panel wide"><h2>${t('loadingPreview')}</h2>${loadingMarkup()}</section><section class="panel library-panel wide"><h2>${t('interaction')}</h2><table class="state-table"><thead><tr><th>${t('state')}</th><th>${t('behavior')}</th></tr></thead><tbody>${(state.lang==='vi'?[['Rê chuột','Bề mặt đổi nhẹ; thao tác luôn hiện.'],['Bàn phím','Viền xanh 2 px, cách điều khiển 3 px; Esc đóng hộp thoại.'],['Đã chọn','Nền xanh nhạt và dấu chọn; không chỉ dựa vào màu.'],['Vô hiệu hóa','Giảm độ đậm, không nhận thao tác.'],['Lỗi','Viền đỏ, hướng dẫn cụ thể ngay dưới trường; giữ nội dung đã nhập.'],['Chuyển động','Phản hồi 100 ms, thanh điều hướng 180 ms; tôn trọng giảm chuyển động.']]:[['Hover','A subtle surface change; actions remain visible.'],['Keyboard','2 px green outline, 3 px offset; Escape closes dialogs.'],['Selected','Soft green surface and checkmark; never color alone.'],['Disabled','Reduced opacity; action is unavailable.'],['Error','Red border and actionable inline text; input is preserved.'],['Motion','100 ms feedback, 180 ms navigation; honors reduced motion.']]).map(([a,b])=>`<tr><td>${a}</td><td>${b}</td></tr>`).join('')}</tbody></table></section></div>`}
function preview(name){if(name==='edit')taskDialog(state.tasks[0]?.id);if(name==='delete')deleteDialog(state.tasks[0]?.id);if(name==='error')taskDialog(undefined,true);if(name==='empty'){state.view='tasks';state.empty=true;state.filter='all';state.search='';history.replaceState(null,'','#tasks');render()}}
if(!['overview','tasks','completed','settings','library','login','register','loggedout'].includes(state.view))state.view='overview';
if(!['light','dark'].includes(state.theme))state.theme='light';
if(!['vi','en'].includes(state.lang))state.lang='vi';
render();

// Stable review fixtures; all use this existing design preview and shell.
const designState=params.get('state');
if(['loading','list-error'].includes(designState)){state.view='tasks';state.listState=designState==='loading'?'loading':'error';render()}
if(designState==='create')taskDialog();
if(designState==='edit')taskDialog(1);
if(designState==='delete')deleteDialog(1);
if(designState==='invalid')taskDialog(undefined,true);
if(designState==='save-error')taskDialog(1,false,'error');
if(designState==='saving')taskDialog(1,false,'saving');
if(designState==='success')toast(t('saved'),true);
if(designState==='empty'){state.view='tasks';state.empty=true;render()}
if(designState==='no-results'){state.view='tasks';state.search=state.lang==='vi'?'Không có kết quả':'No matching result';render()}
if(designState==='completed-empty'){state.view='completed';state.empty=true;render()}
if(designState==='auth-invalid'&&$('#auth-form'))submitAuth({preventDefault(){},currentTarget:$('#auth-form')});
if(['auth-error','auth-loading','registered'].includes(designState)){if(!['login','register'].includes(state.view))state.view='login';state.authState=designState==='registered'?'success':designState==='auth-loading'?'loading':'error';render()}
