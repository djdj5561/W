interface WrongQuestion {
  id: number
  subject: string
  chapter: string
  question: string
  reason: string
  date: string
  reviewed: boolean
}

@Entry
@Component
struct Index {
  @State currentTab: number = 0
  @State searchText: string = ''
  @State currentFilter: string = '全部'
  @State showAddDialog: boolean = false
  @State inputQuestion: string = ''
  @State inputSubject: string = '数学'
  @State inputChapter: string = ''
  @State inputReason: string = ''

  @State questions: WrongQuestion[] = [
    {
      id: 1,
      subject: '数学',
      chapter: '二次函数',
      question: '求函数 y = x² - 4x + 3 的最小值',
      reason: '忽略了顶点公式中的负号，代入时把 -b/2a 算成了正数。',
      date: '今天',
      reviewed: false
    },
    {
      id: 2,
      subject: '英语',
      chapter: '时态与语态',
      question: 'She ____ (finish) her homework before dinner.',
      reason: '没有注意 before 引导的时间先后，误用了一般现在时。',
      date: '昨天',
      reviewed: false
    },
    {
      id: 3,
      subject: '物理',
      chapter: '牛顿运动定律',
      question: '物体受力分析：斜面上的木块',
      reason: '受力图中漏画了斜面对物体的支持力。',
      date: '10月12日',
      reviewed: true
    },
    {
      id: 4,
      subject: '数学',
      chapter: '平面几何',
      question: '证明三角形两边中点连线性质',
      reason: '辅助线画出后，没有检查三角形相似的对应边顺序。',
      date: '10月11日',
      reviewed: false
    }
  ]

  private get visibleQuestions(): WrongQuestion[] {
    let result: WrongQuestion[] = this.questions
    if (this.currentTab === 2) {
      result = result.filter((item: WrongQuestion) => !item.reviewed)
    }
    if (this.currentFilter !== '全部') {
      result = result.filter((item: WrongQuestion) => item.subject === this.currentFilter)
    }
    if (this.searchText.trim().length > 0) {
      const keyword: string = this.searchText.trim().toLowerCase()
      result = result.filter((item: WrongQuestion) =>
        item.question.toLowerCase().includes(keyword) ||
        item.reason.toLowerCase().includes(keyword) ||
        item.chapter.toLowerCase().includes(keyword) ||
        item.subject.toLowerCase().includes(keyword)
      )
    }
    return result
  }

  private get pageTitle(): string {
    if (this.currentTab === 1) return '错题知识库'
    if (this.currentTab === 2) return '今日复习'
    return '错题原因档案'
  }

  private addQuestion(): void {
    if (this.inputQuestion.trim().length === 0 || this.inputReason.trim().length === 0) return
    const newQuestion: WrongQuestion = {
      id: Date.now(),
      subject: this.inputSubject,
      chapter: this.inputChapter.trim().length > 0 ? this.inputChapter : '未分类',
      question: this.inputQuestion,
      reason: this.inputReason,
      date: '刚刚',
      reviewed: false
    }
    this.questions = [newQuestion, ...this.questions]
    this.inputQuestion = ''
    this.inputChapter = ''
    this.inputReason = ''
    this.showAddDialog = false
    this.currentTab = 1
    this.currentFilter = '全部'
  }

  private markReviewed(id: number): void {
    this.questions = this.questions.map((item: WrongQuestion) => {
      if (item.id === id) {
        return {
          id: item.id,
          subject: item.subject,
          chapter: item.chapter,
          question: item.question,
          reason: item.reason,
          date: item.date,
          reviewed: true
        }
      }
      return item
    })
  }

  private subjectColor(subject: string): string {
    if (subject === '数学') return '#D65A3A'
    if (subject === '英语') return '#327A68'
    if (subject === '物理') return '#4969A5'
    return '#8065A8'
  }

  build() {
    Stack() {
      Column() {
        Row() {
          Column({ space: 4 }) {
            Text('错因档案').fontSize(13).fontColor('#68716B')
            Text(this.pageTitle).fontSize(25).fontWeight(FontWeight.Bold).fontColor('#202922')
          }.alignItems(HorizontalAlign.Start)
          Blank()
          Button('+')
            .width(44).height(44).fontSize(26).fontColor('#FFFFFF')
            .backgroundColor('#286B58').borderRadius(14)
            .onClick(() => { this.showAddDialog = true })
        }
        .width('100%').padding({ left: 22, right: 22, top: 18, bottom: 16 })

        if (this.currentTab === 0) {
          this.buildOverview()
        } else {
          Row() {
            TextInput({ placeholder: '搜索题目、知识点或错误原因', text: this.searchText })
              .placeholderColor('#87908A').fontSize(14).backgroundColor('#FFFFFF')
              .borderRadius(12).layoutWeight(1)
              .onChange((value: string) => { this.searchText = value })
          }.margin({ left: 20, right: 20, bottom: 12 })
          this.buildFilters()
          Scroll() {
            Column({ space: 12 }) {
              ForEach(this.visibleQuestions, (item: WrongQuestion) => {
                this.questionCard(item)
              }, (item: WrongQuestion) => item.id.toString())
              if (this.visibleQuestions.length === 0) {
                Column({ space: 8 }) {
                  Text('这里还没有错题').fontSize(16).fontWeight(FontWeight.Medium).fontColor('#344139')
                  Text('试试调整搜索内容，或添加一道错题。').fontSize(13).fontColor('#78817B')
                }
                .width('100%').padding(30).alignItems(HorizontalAlign.Center)
              }
            }.padding({ left: 20, right: 20, top: 4, bottom: 20 })
          }.layoutWeight(1)
        }

        this.buildTabBar()
      }
      .width('100%').height('100%').backgroundColor('#F5F6F1')

      if (this.showAddDialog) {
        this.addDialog()
      }
    }
    .width('100%').height('100%')
  }

  @Builder
  private buildOverview() {
    Scroll() {
      Column({ space: 18 }) {
        Row() {
          Column({ space: 8 }) {
            Text('把每一次出错，').fontSize(23).fontWeight(FontWeight.Bold).fontColor('#FFFFFF')
            Text('变成下一次答对的线索。').fontSize(17).fontColor('#DDEAE3')
            Text('从错因出发，找到真正需要补上的知识。')
              .fontSize(12).fontColor('#C5D8CE').margin({ top: 5 })
          }.alignItems(HorizontalAlign.Start)
          Blank()
          Text('✳').fontSize(38).fontColor('#F1C77B')
        }
        .width('100%').padding(20).backgroundColor('#286B58').borderRadius(18)

        Row({ space: 10 }) {
          this.statBlock('累计错题', this.questions.length.toString(), '#E7EFEA')
          this.statBlock('待复习', this.questions.filter((item: WrongQuestion) => !item.reviewed).length.toString(), '#F3E9D7')
          this.statBlock('已掌握', this.questions.filter((item: WrongQuestion) => item.reviewed).length.toString(), '#E5EAF3')
        }.width('100%')

        Row() {
          Text('最近记录').fontSize(18).fontWeight(FontWeight.Bold).fontColor('#253129')
          Blank()
          Text('查看全部  ›').fontSize(13).fontColor('#286B58').onClick(() => { this.currentTab = 1 })
        }.width('100%')

        Column({ space: 12 }) {
          ForEach(this.questions.slice(0, 2), (item: WrongQuestion) => {
            this.questionCard(item)
          }, (item: WrongQuestion) => item.id.toString())
        }
      }.padding({ left: 20, right: 20, top: 2, bottom: 20 })
    }.layoutWeight(1)
  }

  @Builder
  private statBlock(label: string, value: string, color: string) {
    Column({ space: 7 }) {
      Text(value).fontSize(24).fontWeight(FontWeight.Bold).fontColor('#26342C')
      Text(label).fontSize(12).fontColor('#68736B')
    }
    .alignItems(HorizontalAlign.Start).layoutWeight(1).padding(14)
    .backgroundColor(color).borderRadius(14)
  }

  @Builder
  private buildFilters() {
    Row({ space: 8 }) {
      ForEach(['全部', '数学', '英语', '物理'], (item: string) => {
        Button(item)
          .height(32).fontSize(13)
          .fontColor(this.currentFilter === item ? '#FFFFFF' : '#526057')
          .backgroundColor(this.currentFilter === item ? '#286B58' : '#FFFFFF')
          .borderRadius(16)
          .onClick(() => { this.currentFilter = item })
      }, (item: string) => item)
    }.width('100%').padding({ left: 20, right: 20, bottom: 12 })
  }

  @Builder
  private questionCard(item: WrongQuestion) {
    Column({ space: 11 }) {
      Row() {
        Text(item.subject)
          .fontSize(12).fontWeight(FontWeight.Medium).fontColor(this.subjectColor(item.subject))
          .padding({ left: 9, right: 9, top: 5, bottom: 5 })
          .backgroundColor('#F0F3EF').borderRadius(8)
        Text(item.chapter).fontSize(12).fontColor('#747E76').margin({ left: 8 })
        Blank()
        Text(item.date).fontSize(11).fontColor('#909891')
      }
      Text(item.question).fontSize(15).fontWeight(FontWeight.Medium).fontColor('#27332B').maxLines(2)
      Row({ space: 8 }) {
        Text('错因').fontSize(12).fontWeight(FontWeight.Bold).fontColor('#B75E45')
        Text(item.reason).fontSize(12).fontColor('#626D65').layoutWeight(1).maxLines(2)
      }
      .width('100%').padding(11).backgroundColor('#F7F5EF').borderRadius(10)
      if (this.currentTab === 2 && !item.reviewed) {
        Button('标记已掌握')
          .width('100%').height(38).fontSize(13).fontColor('#FFFFFF')
          .backgroundColor('#286B58').borderRadius(10)
          .onClick(() => { this.markReviewed(item.id) })
      }
    }
    .width('100%').padding(15).backgroundColor('#FFFFFF').borderRadius(15)
  }

  @Builder
  private buildTabBar() {
    Row() {
      this.tabItem('⌂', '首页', 0)
      this.tabItem('▤', '知识库', 1)
      this.tabItem('✓', '复习', 2)
    }
    .width('100%').height(62).backgroundColor('#FFFFFF')
    .border({ width: { top: 1 }, color: '#E8EBE6' })
  }

  @Builder
  private tabItem(icon: string, label: string, index: number) {
    Column({ space: 4 }) {
      Text(icon).fontSize(20).fontColor(this.currentTab === index ? '#286B58' : '#89928C')
      Text(label).fontSize(11).fontColor(this.currentTab === index ? '#286B58' : '#89928C')
    }
    .layoutWeight(1).height('100%').justifyContent(FlexAlign.Center)
    .onClick(() => {
      this.currentTab = index
      this.searchText = ''
    })
  }

  @Builder
  private addDialog() {
    Column() {
      Column({ space: 14 }) {
        Row() {
          Text('新增错题').fontSize(19).fontWeight(FontWeight.Bold).fontColor('#253129')
          Blank()
          Text('✕').fontSize(18).fontColor('#78817B').onClick(() => { this.showAddDialog = false })
        }.width('100%')

        Row({ space: 8 }) {
          ForEach(['数学', '英语', '物理'], (item: string) => {
            Button(item)
              .height(34).layoutWeight(1).fontSize(13)
              .fontColor(this.inputSubject === item ? '#FFFFFF' : '#526057')
              .backgroundColor(this.inputSubject === item ? '#286B58' : '#F1F3EF')
              .borderRadius(10)
              .onClick(() => { this.inputSubject = item })
          }, (item: string) => item)
        }

        TextInput({ placeholder: '题目内容', text: this.inputQuestion })
          .height(44).fontSize(14).backgroundColor('#F5F6F1').borderRadius(10)
          .onChange((value: string) => { this.inputQuestion = value })
        TextInput({ placeholder: '所属章节或知识点', text: this.inputChapter })
          .height(44).fontSize(14).backgroundColor('#F5F6F1').borderRadius(10)
          .onChange((value: string) => { this.inputChapter = value })
        TextInput({ placeholder: '这道题为什么做错？', text: this.inputReason })
          .height(44).fontSize(14).backgroundColor('#F5F6F1').borderRadius(10)
          .onChange((value: string) => { this.inputReason = value })

        Button('保存到知识库')
          .width('100%').height(46).fontSize(15).fontColor('#FFFFFF')
          .backgroundColor('#286B58').borderRadius(12)
          .onClick(() => { this.addQuestion() })
      }
      .width('100%').padding(20).backgroundColor('#FFFFFF').borderRadius(18)
    }
    .width('100%').height('100%').padding({ left: 24, right: 24 })
    .justifyContent(FlexAlign.Center).backgroundColor('#66000000')
  }
}
