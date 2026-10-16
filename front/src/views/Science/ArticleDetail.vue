<template>
  <div class="article-detail-page">
    <!-- Back Button -->
    <div class="back-bar">
      <button class="back-btn" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </button>
    </div>

    <!-- Article Container -->
    <div class="article-container" v-if="article">
      <!-- Article Header -->
      <div class="article-header">
        <div class="article-meta">
          <el-tag size="small">{{ getCategoryLabel(article.category) }}</el-tag>
          <span class="dot">·</span>
          <span class="publish-date">{{ article.publishDate }}</span>
          <span class="dot">·</span>
          <span class="read-count">
            <el-icon><View /></el-icon>
            {{ article.readCount }} 阅读
          </span>
        </div>
        <h1 class="article-title">{{ article.title }}</h1>
      </div>

      <!-- Article Cover -->
      <div class="article-cover">
        <img :src="article.cover" :alt="article.title" />
      </div>

      <!-- Article Body -->
      <div class="article-body" v-html="article.content"></div>

      <!-- Article Footer -->
      <div class="article-footer">
        <div class="share-actions">
          <span class="share-label">分享到：</span>
          <el-button text @click="shareTo('weibo')">
            <el-icon><Share /></el-icon>
            微博
          </el-button>
          <el-button text @click="shareTo('wechat')">
            <el-icon><Connection /></el-icon>
            微信
          </el-button>
          <el-button text @click="shareTo('copy')">
            <el-icon><DocumentCopy /></el-icon>
            复制链接
          </el-button>
        </div>

        <!-- Related Articles -->
        <div class="related-articles" v-if="relatedArticles.length">
          <h3 class="related-title">相关推荐</h3>
          <div class="related-grid">
            <div
              v-for="related in relatedArticles"
              :key="related.id"
              class="related-card"
              @click="goToArticle(related)"
            >
              <div class="related-image">
                <img :src="related.cover" :alt="related.title" />
              </div>
              <div class="related-info">
                <span class="related-category">{{ getCategoryLabel(related.category) }}</span>
                <h4>{{ related.title }}</h4>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="article-nav">
          <button class="nav-btn prev" @click="goToPrev" v-if="prevArticle">
            <el-icon><ArrowLeft /></el-icon>
            <span>上一篇：{{ prevArticle.title }}</span>
          </button>
          <button class="nav-btn next" @click="goToNext" v-if="nextArticle">
            <span>下一篇：{{ nextArticle.title }}</span>
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>
      </div>
    </div>

    <!-- Not Found -->
    <div class="not-found" v-else>
      <el-empty description="文章不存在或已被删除" />
      <el-button type="primary" @click="$router.push('/science')">返回科普列表</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  ArrowRight,
  View,
  Share,
  Connection,
  DocumentCopy
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const article = ref(null)
const allArticles = ref([])

const currentIndex = computed(() =>
  allArticles.value.findIndex(a => a.id === Number(route.params.id))
)

const relatedArticles = computed(() => {
  if (!article.value) return []
  return allArticles.value
    .filter(a => a.id !== Number(route.params.id) && a.category === article.value.category)
    .slice(0, 3)
})

const prevArticle = computed(() =>
  currentIndex.value > 0 ? allArticles.value[currentIndex.value - 1] : null
)

const nextArticle = computed(() =>
  currentIndex.value < allArticles.value.length - 1
    ? allArticles.value[currentIndex.value + 1]
    : null
)

function getCategoryLabel(category) {
  const labels = {
    culture: '文化',
    history: '历史',
    education: '教育',
    life: '生活'
  }
  return labels[category] || category
}

function loadArticle() {
  const id = Number(route.params.id)
  // Find from allArticles (which includes the full articles data)
  const found = allArticles.value.find(a => a.id === id)
  if (found) {
    article.value = found
    document.title = `${found.title} — 掌言`
  }
}

function goBack() {
  if (window.history.length > 2) {
    router.back()
  } else {
    router.push('/science')
  }
}

function goToArticle(related) {
  router.push(`/science/${related.id}`)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToPrev() {
  if (prevArticle.value) {
    router.push(`/science/${prevArticle.value.id}`)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function goToNext() {
  if (nextArticle.value) {
    router.push(`/science/${nextArticle.value.id}`)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function shareTo(platform) {
  switch (platform) {
    case 'weibo':
      ElMessage.success('已打开微博分享')
      break
    case 'wechat':
      ElMessage.info('请截图分享到微信')
      break
    case 'copy':
      navigator.clipboard.writeText(window.location.href)
      ElMessage.success('链接已复制')
      break
  }
}

onMounted(() => {
  // Load all articles data from the Science page module
  // We inline the full articles array here for simplicity
  allArticles.value = [
    {
      id: 1,
      title: '中国手语发展简史：从手势到规范化的历程',
      description: '本文介绍了中国手语从古代手语到现代规范化手语的演变过程，以及聋人教育的发展历程。',
      cover: 'https://picsum.photos/800/400?random=1',
      category: 'history',
      readCount: 1256,
      publishDate: '2026-04-20',
      isFeatured: true,
      content: `
        <h2>中国手语的起源</h2>
        <p>中国手语的历史可以追溯到古代。在古代中国，聋人通过手势进行交流，逐渐形成了一套相对完整的手势系统。</p>
        <h2>近代手语教育</h2>
        <p>19世纪末20世纪初，随着西方传教士的到来，现代聋人教育开始在中国发展。上海、北京等地相继建立了聋人学校，开始系统地教授手语。</p>
        <h2>新中国手语规范化</h2>
        <p>新中国成立后，中国聋人协会组织专家对各地手语进行调研，于1959年出版了《聋人通用手语图》，开始推行统一的手语标准。</p>
        <h2>现代手语发展</h2>
        <p>改革开放后，中国手语研究进入新阶段。2008年，北京残奥会将中国手语推向世界舞台；2018年，《国家通用手语方案》正式发布，标志着中国手语规范化进入新时代。</p>
      `
    },
    {
      id: 2,
      title: '为什么学习手语？聋人文化与包容社会',
      description: '手语不仅是沟通工具，更是聋人文化的重要组成部分。学习手语是对聋人群体的尊重，也是构建包容社会的重要一步。',
      cover: 'https://picsum.photos/800/400?random=2',
      category: 'culture',
      readCount: 986,
      publishDate: '2026-04-18',
      content: `
        <h2>手语是独立的语言</h2>
        <p>手语是一种完整的自然语言，有自己的语法、词汇和表达方式。它不是口语的简单翻译，而是聋人社区自然发展形成的语言系统。</p>
        <h2>手语与聋人文化</h2>
        <p>对于许多聋人来说，手语是他们认同感和归属感的重要来源。手语文化包括独特的幽默、艺术、诗歌等形式。</p>
        <h2>学习手语的意义</h2>
        <p>学习手语不仅可以帮助你与聋人朋友交流，还能增进对聋人文化的理解，促进社会的包容与和谐。</p>
      `
    },
    {
      id: 3,
      title: '手指字母：用手拼写的艺术',
      description: '手指字母是用手指形状表示汉语拼音字母的特殊方式，是手语的重要组成部分。本文介绍手指字母的起源和使用方法。',
      cover: 'https://picsum.photos/800/400?random=3',
      category: 'education',
      readCount: 756,
      publishDate: '2026-04-15',
      content: `
        <h2>什么是手指字母</h2>
        <p>手指字母（finger spelling）是使用手指形状来表示字母的一种方法，主要用于拼写人名、地名等专有名词，以及手语中没有对应手势的词汇。</p>
        <h2>手指字母的由来</h2>
        <p>手指字母最早源于欧洲的修道院手语，后经过不断完善，在18世纪传入中国，形成了具有中国特色的手指字母系统。</p>
        <h2>如何学习手指字母</h2>
        <p>学习手指字母需要掌握每个字母对应的手势，并练习连续拼写。初学者可以先从简单的字母和单词开始，逐步提高速度。</p>
      `
    },
    {
      id: 4,
      title: '聋人艺术家：用双手舞动人生',
      description: '许多聋人艺术家通过手语创作出令人惊叹的艺术作品，包括手语诗歌、手语舞蹈等，展现了聋人文化的独特魅力。',
      cover: 'https://picsum.photos/800/400?random=4',
      category: 'culture',
      readCount: 623,
      publishDate: '2026-04-12',
      content: `
        <h2>手语诗歌</h2>
        <p>手语诗歌是一种独特的艺术形式，通过手势、表情和身体动作的配合，创造出富有韵律和意境的表达。</p>
        <h2>手语舞蹈</h2>
        <p>手语舞蹈将手语动作与舞蹈元素结合，创造出独特的视觉艺术效果，深受观众喜爱。</p>
        <h2>聋人艺术家代表</h2>
        <p>中国有许多优秀的聋人艺术家，他们用手语创作出精彩的作品，为推广手语文化做出了重要贡献。</p>
      `
    },
    {
      id: 5,
      title: '如何与聋人有效沟通：实用技巧指南',
      description: '与聋人沟通需要注意什么？本文提供了一些实用的沟通技巧，帮助你更好地与聋人朋友交流。',
      cover: 'https://picsum.photos/800/400?random=5',
      category: 'life',
      readCount: 1589,
      publishDate: '2026-04-10',
      content: `
        <h2>基本沟通技巧</h2>
        <p>与聋人沟通时，保持面对对方、说话清晰、使用自然手势是很重要的。同时，注意光线和角度，确保对方能清楚看到你的手势和表情。</p>
        <h2>使用辅助工具</h2>
        <p>现代技术为聋人沟通提供了很多便利，如助听器、人工耳蜗、文字输入软件等。了解这些工具可以帮助你更好地与聋人沟通。</p>
        <h2>尊重与理解</h2>
        <p>最重要的是保持尊重和理解的态度。每个人都有自己的交流偏好，了解对方的习惯，用心沟通。</p>
      `
    },
    {
      id: 6,
      title: '世界手语日：全球聋人社区的共同节日',
      description: '每年9月的最后一个星期日是世界手语日。了解这个特殊日子的由来和意义，以及全球聋人社区如何庆祝。',
      cover: 'https://picsum.photos/800/400?random=6',
      category: 'culture',
      readCount: 445,
      publishDate: '2026-04-08',
      content: `
        <h2>世界手语日的由来</h2>
        <p>世界手语日起源于1958年的国际聋人节。2017年，联合国正式宣布将每年9月的最后一个星期日定为世界手语日。</p>
        <h2>庆祝活动</h2>
        <p>在世界手语日，全球各地会举办各种活动，包括手语工作坊、文化展示、宣传教育等，提高公众对手语的认识。</p>
        <h2>中国的手语日</h2>
        <p>中国也会在每年九月的第四周举办"手语日"相关活动，推动手语普及和社会关注。</p>
      `
    },
    {
      id: 7,
      title: '听障口语者VS听障手语者，你了解多少？',
      description: '当我们想理解或帮助一个群体的时候，我们首先需要"了解"这个群体——理解建立在了解之上，以此为基础的尊重才是真正的尊重。',
      cover: 'https://picsum.photos/800/400?random=7',
      category: 'culture',
      readCount: 0,
      publishDate: '2026-04-27',
      content: `
        <p style="font-size:15px;color:#555;line-height:1.9;margin-bottom:20px;padding:16px;background:#f9f9f9;border-left:4px solid #409eff;border-radius:4px;">
          当我们想理解或帮助一个群体的时候，我们首先需要"了解"这个群体——理解建立在了解之上，以此为基础的尊重才是真正的尊重。
        </p>

        <p style="margin-bottom:16px;">"Deaf culture"一直以来被直译为"聋人文化"，在中国，很多人更是将"Deaf-聋人"一词理解为全体听力残疾人，认为这部分人群听不到也不会说。但实际上，随着辅具和康复的进步，越来越多听力残疾人可以口语交流，他们是听障口语者——Hard of Hearing，两者在交流方式和各自文化上有很大的区别。</p>

        <p style="margin-bottom:24px;">这篇来源于残障之声的文章，对到底什么是"聋人文化"进行了详细解读，文章中附录：中国聋人协会整理编辑的"与听力残疾人相处小常识"，希望对大家更全面客观的了解听障群体有所帮助。</p>

        <h2>一、"deaf culture"的翻译</h2>

        <p style="margin-bottom:16px;">"聋人文化"是舶来品，英语原文是"deaf culture"，直译就是"聋人文化"。实事求是地说，这个翻译是非常不负责任的。为什么这么说呢？</p>

        <h2>二、"聋"到底是指什么？</h2>

        <p style="margin-bottom:16px;">首先说"deaf"这个词，直译是"聋人"。但是，不同的国家对其的指代是不同的。</p>

        <p style="margin-bottom:16px;">在英语国家，有这样一个组织，英文名是"World Federation of the Deaf"，翻译为"世界聋人联合会"。它成立于1951年。在"世界聋人联合会"官方网站中可以了解到，其中"deaf"这个词，对应的是指<strong>以手语为主要交流语言</strong>的听力残疾人。</p>

        <p style="margin-bottom:16px;">但在中国，社会大众则将"聋人"一词理解为全体听力残疾人。</p>

        <h2>三、"重听"真的只是听力损失比较轻吗？</h2>

        <p style="margin-bottom:16px;">1977年，另一个组织"International Federation of Hard Of Hearing People"成立了，翻译为"世界听障者联盟"。注意这里对应中文的"聋人"是"hard of hearing"，不是"deaf"。</p>

        <p style="margin-bottom:16px;">那么"hard of hearing"，为什么不翻译为"世界重听联盟"呢？</p>

        <p style="margin-bottom:16px;">因为在汉语释义中，"重听"指听力下降，听音失真，为耳聋之轻症。而在"世界听障者联盟"的官方网站中可以知道，世界听障者联盟是包括听力损失程度很重，但仍然选择口语或书面语为主要交流语言的听力残疾人。</p>

        <p style="margin-bottom:16px;">1991年，这两个机构共同签署了一个声明，对英文称谓做了进一步的规范和说明。</p>

        <p style="margin-bottom:16px;">在中国，官方称谓是"听力残疾人"，"聋人"是通俗称谓。</p>

        <p style="margin-bottom:16px;color:#e6a23c;font-weight:500;">注意：用"聋哑人"指代手语者或听力残疾人是不正确的，是有歧视色彩的称呼，应该禁止。同时，在英语国家，也基本不用"deaf-mute"（聋哑）这个词来称呼听力残疾人。</p>

        <p style="margin-bottom:16px;"><strong>中国聋人协会章程</strong>中有释义：</p>

        <p style="margin-bottom:16px;padding:12px 16px;background:#f0f9eb;border-radius:4px;font-weight:500;">
          聋人（含听力言语残疾人、言语残疾人、重听、耳蜗植入者）。
        </p>

        <p style="margin-bottom:16px;">和聋人有关的社会团体是"中国聋人协会"。它也是"世界聋人联合会"和"世界听障者联盟"的会员。</p>

        <h2>四、小结</h2>

        <div style="padding:20px;background:#f0f9eb;border-radius:8px;margin-bottom:24px;">
          <p style="margin-bottom:8px;"><strong>综上所述，在英语国家：</strong></p>
          <ul style="line-height:2;padding-left:20px;">
            <li><strong>聋人 = Deaf = 手语者</strong></li>
            <li><strong>听障者 = Hard of Hearing = 口语者</strong>（包括书面语使用者）</li>
          </ul>
          <p style="margin-top:12px;margin-bottom:0;">同理"deaf culture"，应该是以手语为主要交流语言的听力残疾人的"culture"。以口语为主要交流语言的听力残疾人更加侧重于全面康复和辅具提升等内容。</p>
        </div>

        <p style="margin-bottom:16px;">可以看出，对于听力残疾人群体，英语国家是完全以使用语言而非听力损失程度界定的，从而有针对性地提供精准服务，并开展相应的活动。</p>

        <h2>五、此culture非彼文化</h2>

        <p style="margin-bottom:16px;">再说第二个词"culture"，名词的中文直译是"文化，文明（指国家或群体的风俗、信仰、艺术、生活方式及社会组织）；文化（指拥有特定信仰等的国家、群体等）；文化（艺术、音乐、文学等的统称）"。</p>

        <p style="margin-bottom:16px;">而中文"文化"的释义有三个：</p>
        <ol style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>人类在社会历史发展过程中所创造的物质财富和精神财富的总和，特指精神财富，如文学、艺术、教育、科学等。</li>
          <li>考古学用语，指同一个历史时期的不依分布地点为转移的遗迹、遗物的综合体。同样的工具、用具，同样的制造技术等，是同一种文化的特征。</li>
          <li>指运用文字的能力及一般知识。</li>
        </ol>

        <p style="margin-bottom:16px;">再看看"deaf culture"的相关内容，用中文语境来表述，大都是跟手语相关的艺术创作内容，和以手语为主要交流语言的听力残疾人的信息无障碍内容。</p>

        <h2>六、总结</h2>

        <div style="padding:20px;background:#fef0f0;border-radius:8px;margin-bottom:24px;">
          <p style="margin-bottom:12px;">因此，在引用或是看到"聋人文化"这个词时，呼吁大家一定要留意词汇背后的来源和背景，深究英语原文词汇，明确：</p>
          <ul style="line-height:2;padding-left:20px;">
            <li><strong>"deaf culture"</strong>是以手语为主要交流语言的听力残疾人的信息无障碍需求</li>
            <li>注意以科学专业的态度来科普</li>
          </ul>
          <p style="margin-top:12px;margin-bottom:0;">这才是比较负责任的做法。</p>
        </div>

        <p style="margin-bottom:16px;">特校老师和手语翻译更应需要了解全面信息，才能更好、更精准地理解所服务的听力残疾人。</p>

        <p style="margin-bottom:24px;">经过反复调研和倾听大家的呼声，参考国内外相关信息，中国聋协于2017年开创性地提出<strong>"听力残疾口语使用者"</strong>和<strong>"听力残疾手语使用者"</strong>的细化分类。听力残疾口语使用者也叫<strong>听障口语者</strong>，对应英语的"hard of hearing"；听力残疾手语使用者也叫<strong>听障手语者</strong>，对应英语的"deaf"，跟国外的称谓完全一致，这样也便于从工作层面开展更为精准的服务。</p>

        <h2>附录：与听力残疾人相处小常识</h2>

        <p style="margin-bottom:16px;">以下为中国聋人协会整理编辑的"与听力残疾人相处小常识"，便于加深理解。</p>

        <h3 style="font-size:17px;margin-bottom:12px;color:#0d0d0d;">一、对使用手语的听力残疾人</h3>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">环境</h4>
        <p style="margin-bottom:8px;">他们靠视觉识别语言，所以照明在语言交流中很重要。</p>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>请在明亮的场所对他们说话，他们会因为黑暗而看不见手语。</li>
          <li>请让光线衬托出您的面部表情和手的动作，他们会因为光线刺眼而看不清手语。</li>
          <li>您和他们的对话空间中，请保持空无一物；比如说，如果在圆形会议桌或者餐厅圆桌中间放花篮或花瓶等，他们会因为中间的遮挡物而看不见圆桌对面人的手语。</li>
        </ul>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">手语</h4>
        <p style="margin-bottom:8px;"><strong>了解手语作为视觉语言的特征：</strong></p>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>学会一点手语，会让他们感觉更亲近。</li>
          <li>如果您不谙手语，请以笔谈方式交流；比如主动提出用纸笔、手机输入、电脑录入。</li>
          <li>如果您会手语，在对话时，要注意表情与所说的事情相符，还要注意不要由于心情不好将情绪表露出来。</li>
          <li>请看着他们的眼睛说话，尤其是看他们手语的时候，不要东张西望。如果确实需要转移视线，要以表情或动作告知。</li>
          <li>有些先天失聪的使用手语者，在使用手语时，伴随手势表达的需要，口部会有相应动作配合（术语称之为"口动"），这是手语这门语言的特点。只是有些人由于对声音的掌控不好，口动的时候，会发出一些异常的声音，这时如果环境不合适（比如重要会议需要安静的情况下），请悄悄的指着嗓子告诉他"噤声"以示提醒。</li>
          <li>他们单独组织会议或者活动的时候，有时候会出现大家举起双手摆动的场面，这种情况，国际上手语使用者活动的场合也很多见，这是他们根据群体不能听的特点，形成的视觉接收的"鼓掌"方式。要了解和说明他们这个特点。</li>
          <li>他们相互交流使用手语时，有时候会因为自己听不见，并不知道在聊得兴起时，发出了一些奇怪的声音或尖叫，如果您是参与他们聊天的，请对他们发出的异常声音给予充分的理解和谅解。</li>
        </ul>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">礼仪</h4>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>当他们来办事，您带他们去有关负责部门并为他做手语翻译的时候，在与办事人员口语交流的同时，也请尽量用手语翻译刚才说的内容，避免他们误会您说的口语与他的手语有出入。</li>
          <li>他们有些人，倾诉欲望很强，或者由于听不见好奇心很强，如果他们感觉您友善，会不停的与您打着手语倾诉或提问题，这个时候不要不耐烦的排斥。可以礼貌的告诉他们您忙，他们一般会给予理解并感谢您。</li>
          <li>与他们在一起的时候，若条件允许，尽可能向他们翻译您所听到的一切，无论是用手语还是文字，会很受他们欢迎。</li>
          <li>如果需要向他们打招呼或提醒他们，当他们背对着您时，请轻轻拍几下他们肩膀、胳膊或背部，不要碰身体其他部位；当双方面对面时，挥挥手引起他们的注意。</li>
          <li>若是室内召集的会议，会议间歇再重新开始时，他们可能因为利用间歇在座位上互相聊天而看不见会议主持人的举动，这个时候可以连续按动室内电灯开关，以光线的变化提醒他们会议开始。</li>
        </ul>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">手语翻译</h4>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>他们参加会议需要的手语翻译必须请当地聋协推荐，切忌越俎代庖，特别是用外地手语翻译给本地做手语翻译。因为本地手语翻译情况了解，有用人保证。外地翻译为人等情况不了解有风险。</li>
          <li>重要会场或讲座翻译的时候，不要中间老是问他们看明白吗？可以寻找适当的机会，比如在会后方便时，听取他们对翻译质量的意见。</li>
          <li>忌安排使用口语且会手语的听力残疾人在重要场合作为手语翻译。因为他们的听力也不好。一对一或一对二、三的场合可以协助作手语翻译工作。</li>
        </ul>

        <h3 style="font-size:17px;margin-bottom:12px;color:#0d0d0d;">二、对使用口语的听力残疾人</h3>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">环境</h4>
        <p style="margin-bottom:8px;"><strong>避免噪音干扰，提供良好照明。</strong></p>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>与他们对话时，请关掉周围音响，或者换到附近安静的角落，若他们人数较多，最好是大家一起换个安静房间。</li>
          <li>若白天房间光线较暗，请打亮灯光，或者大家一起到户外聊天。</li>
          <li>轻松的对话距离在一米左右，别超过两米；因为人工耳蜗和助听器的最佳拾音距离在两米以内，离得太远则会让声音衰减，难以分辨。</li>
          <li>各种讨论会，尽量选择安静的房间，避开嘈杂的餐厅、容易产生回声和混响的大型会议室。身为会务组织者，请主动询问他们是否需要将座位调整到主讲人和其他主要发言人附近，是否需要将拾音外挂放在主讲人旁边。</li>
        </ul>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">动作</h4>
        <p style="margin-bottom:8px;"><strong>请让他们看到您的面容和口型：</strong></p>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>如果戴着口罩和墨镜，对话前请取下，以便他们看清您的口型和表情。</li>
          <li>请面对他们说话，表情和您平时习惯的一样就好；唇形清晰有力，没必要故意夸张夸大。不然他们不敢确定您是在与他们对话。</li>
          <li>当打算开始一次对话，如果他们背对着您，请走到他们正面，或者从后方以比较显著的响动走近后，轻轻碰触肩或胳膊，示意想和他们聊一聊；如果您就在他们正前方两三米外，不妨试试呼唤示意；但是在他们很近的身后突然高声呼喊，或者是他们毫无知觉时突然冒出来，都会吓到他们，也比较失礼。</li>
        </ul>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">音质和对话</h4>
        <p style="margin-bottom:8px;"><strong>发音清晰平和，速度和缓，注意双方互动：</strong></p>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>安静环境下，发音清晰，音量比自己平时习惯的高那么一点儿就行，不必刻意拔高嗓门。因为助听辅具（助听器和人工耳蜗）已经调整好了声音补偿额度，大声喊叫只能让他们听起来非常难受，反而无助于提高言语识别率。</li>
          <li>嘈杂环境下，记得和他们稍微沟通一下说话音量是否合宜。如果对方觉得您的声音还是太轻，试试彼此站得更近一点。</li>
          <li>语速比自己平时说的慢一点儿就好，可是太慢也会让对方费解。越自然越好。</li>
          <li>请说普通话，或本地人熟悉的语言。</li>
          <li>如果他们告诉您，刚才提到的某个词或者句子没听清，请您直接换个表达说一遍。</li>
          <li>他们的发音或多或少存在病理性腔调，这是由于听损造成他们听到的声音有缺失，他们的听觉—口语反馈能力比较粗大，不像您那么精细。嘲笑他们的发音，攻击性地问"你说话怎么大舌头"、"你是哪国人"之类问题，都会阻碍交流。</li>
          <li>头几分钟双方对话接不上榫时，您只要继续说就行，等待他们的听觉中枢下载您的语音数据包，进行初始化。熬过了这艰难的头几分钟，会发现谈话质量有改善。要是一看到他们面露困惑神色，就马上掏出纸笔或打手势，完全放弃口头交流，实不可取。</li>
          <li>如果讲到关键信息，强化重音，多重复两遍。</li>
          <li>如果您讲了很长的一段内容，请就关键部分适当向对方提问，以确保你想说的意思传达出去了。</li>
          <li>他们要是实在听不清你在说什么，会根据自己听到的关键词主动提问，对此您一定要正面回答"是"或"不是"。</li>
          <li>如果您和别人聊得特别高兴，他们问"你们在聊什么"，要是能为他们复述大体概要，他们都会非常感谢您。</li>
        </ul>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">各种助听辅具和辅助沟通方式</h4>
        <p style="margin-bottom:8px;"><strong>创造友善的使用环境：</strong></p>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>当面交流时，未经允许，切忌触碰对方佩戴的助听辅具。</li>
          <li>如果他们请你使用蓝牙麦克、FM系统等用于拾音的助听辅具配件，不妨欣然接过夹在衣领上，以便让自己的声音更好地传到他们的助听器和人工耳蜗里，改善谈话效果。</li>
          <li>重要事情请写下来，或者发电子邮件，用微信、短信、QQ留言等方式来提醒确认。</li>
          <li>他们的辨听能力千差万别，有一部分人听力基础较差，使用助听器或人工耳蜗，是为了获取更多声音来辅助交流，他们可能非常依赖看听结合。如果对方提出写字沟通，也请接受这样的请求。</li>
        </ul>

        <h4 style="font-size:15px;margin-bottom:8px;color:#333;">电话、视频、语音留言等远程电子语音沟通</h4>
        <p style="margin-bottom:8px;"><strong>使用前征询对方意见：</strong></p>
        <ul style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li>如果一定要打电话，尽量用手机，少用座机。</li>
          <li>打电话前，请给他们用微信、短信之类发文字留言，提前询问。</li>
          <li>打电话时确保附近噪音不太大，也没有其他人同时在说话。</li>
          <li>部分听力损失较重，重度依赖口型的人，虽然能够当面交流，可是无法接听电话。尽可能选择短信、微信、QQ、面谈等方式，效率更高。对可以接听电话的，尽量用短句，语速平缓。</li>
        </ul>

        <h3 style="font-size:17px;margin-bottom:12px;color:#0d0d0d;">三、综合以上三种情况，普遍需要注意如下4点：</h3>

        <ol style="line-height:2;padding-left:20px;margin-bottom:16px;">
          <li style="margin-bottom:8px;"><strong>平等对待才能建立互相尊重。</strong>拿听力和发音问题调侃对方通常属于失礼之举。</li>
          <li style="margin-bottom:8px;"><strong>无论是和使用手语还是与使用口语的听力残疾人对话，还是当着他们与别人交谈，都务必让对方看到您的表情、口型和手势。</strong></li>
          <li style="margin-bottom:8px;"><strong>当您忙于接待其他人时，看见听力残疾人进来，要以目光示意并点头，表示你知道他来了。</strong></li>
          <li style="margin-bottom:0;"><strong>有听力残疾人参与的会议，必须安排速记服务，</strong>以便他们通过同步字幕更方便准确地获取会议信息。</li>
        </ol>
      `
    }
  ]

  loadArticle()
})
</script>

<style scoped>
.article-detail-page {
  min-height: 100vh;
  background: #fafaf8;
  padding-bottom: 80px;
}

/* Back Bar */
.back-bar {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px 32px 0;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #8a8a8a;
  background: none;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 180ms ease;
}

.back-btn:hover {
  color: #0d0d0d;
  border-color: #c8c8c8;
  background: #fff;
}

/* Article Container */
.article-container {
  max-width: 900px;
  margin: 24px auto 0;
  padding: 0 32px;
}

/* Article Header */
.article-header {
  margin-bottom: 32px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #8a8a8a;
}

.dot {
  color: #dcdfe6;
}

.read-count {
  display: flex;
  align-items: center;
  gap: 4px;
}

.article-title {
  font-size: 32px;
  font-weight: 700;
  color: #0d0d0d;
  letter-spacing: -0.5px;
  line-height: 1.3;
  margin: 0;
}

/* Article Cover */
.article-cover {
  width: 100%;
  height: 420px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 40px;
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Article Body */
.article-body {
  font-size: 16px;
  color: #333;
  line-height: 2;
  margin-bottom: 48px;
}

.article-body :deep(h2) {
  font-size: 22px;
  font-weight: 700;
  color: #0d0d0d;
  margin: 36px 0 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.article-body :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  color: #0d0d0d;
  margin: 28px 0 12px;
}

.article-body :deep(h4) {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 20px 0 10px;
}

.article-body :deep(p) {
  margin-bottom: 16px;
}

.article-body :deep(ul),
.article-body :deep(ol) {
  margin-bottom: 16px;
}

.article-body :deep(li) {
  margin-bottom: 6px;
}

.article-body :deep(strong) {
  color: #0d0d0d;
}

/* Article Footer */
.article-footer {
  padding-top: 32px;
  border-top: 1px solid #e8e8e8;
}

.share-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 48px;
}

.share-label {
  font-size: 14px;
  color: #8a8a8a;
}

/* Related Articles */
.related-articles {
  margin-bottom: 48px;
}

.related-title {
  font-size: 18px;
  font-weight: 600;
  color: #0d0d0d;
  margin: 0 0 20px;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.related-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 180ms ease;
}

.related-card:hover {
  border-color: #c8c8c8;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.related-image {
  height: 120px;
  overflow: hidden;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 300ms ease;
}

.related-card:hover .related-image img {
  transform: scale(1.05);
}

.related-info {
  padding: 14px;
}

.related-category {
  font-size: 11px;
  padding: 2px 6px;
  background: #f0f7ff;
  color: #409eff;
  border-radius: 3px;
  display: inline-block;
  margin-bottom: 6px;
}

.related-info h4 {
  font-size: 13px;
  font-weight: 600;
  color: #0d0d0d;
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Article Navigation */
.article-nav {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #8a8a8a;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 14px 20px;
  cursor: pointer;
  transition: all 180ms ease;
  max-width: 50%;
}

.nav-btn:hover {
  color: #0d0d0d;
  border-color: #c8c8c8;
}

.nav-btn span {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-align: left;
}

.nav-btn.prev {
  margin-right: auto;
}

.nav-btn.next {
  margin-left: auto;
  justify-content: flex-end;
}

/* Not Found */
.not-found {
  max-width: 900px;
  margin: 80px auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

@media (max-width: 768px) {
  .back-bar,
  .article-container {
    padding: 16px 20px 0;
  }

  .article-title {
    font-size: 24px;
  }

  .article-cover {
    height: 240px;
    margin-bottom: 28px;
  }

  .related-grid {
    grid-template-columns: 1fr;
  }

  .article-nav {
    flex-direction: column;
  }

  .nav-btn {
    max-width: 100%;
    width: 100%;
  }

  .nav-btn.next {
    margin-left: 0;
  }
}
</style>
