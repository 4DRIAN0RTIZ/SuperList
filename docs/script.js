const DEFAULT_LANG = 'es';

const LOCALE_PATHS = {
	en: 'locale/en/en.json',
	es: 'locale/es/es.json',
};

const LANG_STORAGE_KEY = 'superlist-lang';

const translations = {};

async function loadTranslations(lang) {
	const requestedLang = LOCALE_PATHS[lang] ? lang : DEFAULT_LANG;

	if (translations[requestedLang]) {
		return { lang: requestedLang, values: translations[requestedLang] };
	}

	try {
		const res = await fetch(LOCALE_PATHS[requestedLang]);
		if (!res.ok) throw new Error(`${LOCALE_PATHS[requestedLang]} returned ${res.status}`);

		const values = await res.json();
		translations[requestedLang] = values;
		return { lang: requestedLang, values };
	} catch (error) {
		console.error(`Unable to load locale for ${requestedLang}`, error);

		if (requestedLang !== DEFAULT_LANG) {
			return loadTranslations(DEFAULT_LANG);
		}

		return { lang: DEFAULT_LANG, values: {} };
	}
}

async function applyTranslations(lang) {
	const { lang: activeLang, values: t } = await loadTranslations(lang);
	document.documentElement.lang = activeLang;
	localStorage.setItem(LANG_STORAGE_KEY, activeLang);

	document.querySelectorAll('[data-i18n]').forEach(el => {
		const key = el.getAttribute('data-i18n');
		if (!(key in t)) return;
		if (el.tagName === 'TITLE') {
			document.title = t[key];
		} else if (el.tagName === 'META') {
			el.setAttribute('content', t[key]);
		} else {
			el.innerHTML = t[key];
		}
	});

	const btn = document.getElementById('lang-toggle');
	if (btn) btn.textContent = activeLang === 'en' ? 'ES' : 'EN';

	await renderRoadmap(activeLang);
}

document.addEventListener('DOMContentLoaded', async () => {
	const saved = localStorage.getItem(LANG_STORAGE_KEY) || DEFAULT_LANG;
	applyTranslations(saved);

	const btn = document.getElementById('lang-toggle');
	if (btn) {
		btn.addEventListener('click', async () => {
			const current = localStorage.getItem(LANG_STORAGE_KEY) || DEFAULT_LANG;
			await applyTranslations(current === 'en' ? 'es' : 'en');
		});
	}

	document.querySelectorAll('.code-block, details.code-details').forEach(block => {
		const header = block.querySelector('.code-header') || block.querySelector('summary');
		const body = block.querySelector('.code-body');
		if (!header || !body) return;

		const copyBtn = document.createElement('button');
		copyBtn.className = 'copy-btn';
		copyBtn.textContent = 'copy';
		copyBtn.addEventListener('click', e => {
			e.preventDefault();
			navigator.clipboard.writeText(body.innerText.trim()).then(() => {
				copyBtn.textContent = 'copied!';
				copyBtn.classList.add('copied');
				setTimeout(() => {
					copyBtn.textContent = 'copy';
					copyBtn.classList.remove('copied');
				}, 1500);
			});
		});
		header.appendChild(copyBtn);
	});

	await Promise.all([
		updateHeroBadgeRelease(),
		loadChangelog(),
	]);
});

const ROADMAP_STATUS_CLASSES = {
	done: 'tag-done',
	planned: 'tag-planned',
	working: 'tag-working',
	idea: 'tag-idea',
};

let roadmapData = null;

async function loadRoadmap() {
	if (roadmapData) return roadmapData;

	const res = await fetch('roadmap.json');
	if (!res.ok) throw new Error(`roadmap.json returned ${res.status}`);

	roadmapData = await res.json();
	return roadmapData;
}

function localizedValue(value, lang) {
	if (typeof value === 'string') return value;
	return value?.[lang] || value?.[DEFAULT_LANG] || '';
}

async function renderRoadmap(lang) {
	const container = document.getElementById('roadmap-content');
	if (!container) return;

	try {
		const roadmap = await loadRoadmap();
		const sections = roadmap.sections || [];

		if (sections.length === 0) {
			renderRoadmapEmpty(container, lang);
			return;
		}

		container.innerHTML = sections.map((section, sectionIndex) => {
			const title = localizedValue(section.title, lang);
			const margin = sectionIndex === 0
				? 'margin-bottom: 1rem;'
				: 'margin-top: 2rem; margin-bottom: 1rem;';
			const items = (section.items || []).map(item => {
				const status = item.status || 'planned';
				const tagClass = ROADMAP_STATUS_CLASSES[status] || ROADMAP_STATUS_CLASSES.planned;
				const statusLabel = localizedValue(roadmap.labels?.[status], lang) || status;
				const text = localizedValue(item.text, lang);
				const ref = item.ref?.url && item.ref?.label
					? `<span class="roadmap-ref"><a href="${escapeHtml(item.ref.url)}" target="_blank" rel="noopener">${escapeHtml(item.ref.label)}</a></span>`
					: '';

				return `
					<div class="roadmap-item">
						<span class="tag ${tagClass}">${escapeHtml(statusLabel)}</span>
						<span>${escapeHtml(text)}</span>
						${ref}
					</div>`;
			}).join('');

			return `
				<h3 style="${margin}">${escapeHtml(title)}</h3>
				<div class="roadmap">${items}</div>`;
		}).join('');
	} catch (error) {
		console.error('Unable to load roadmap', error);
		renderRoadmapEmpty(container, lang);
	}
}

function renderRoadmapEmpty(container, lang) {
	const t = translations[lang] || translations[DEFAULT_LANG] || {};
	const message = t['roadmap-empty-msg'] || 'Roadmap unavailable.';
	container.innerHTML = `<p class="changelog-empty">${message}</p>`;
}

const CHANGELOG_REPO = 'https://github.com/4drian0rtiz/SuperList';

let changelogData = null;

async function loadChangelogData() {
	if (changelogData) return changelogData;

	const res = await fetch('changelog.json');
	if (!res.ok) throw new Error('changelog.json not found');

	changelogData = await res.json();
	return changelogData;
}

async function updateHeroBadgeRelease() {
	const field = document.getElementById('hero-badge-release');
	if (!field) return;

	try {
		const releases = await loadChangelogData();
		const version = releases?.[0]?.version || 'N/A';
		field.textContent = version;
	} catch (error) {
		console.error('Error fetching changelog.json:', error);
		field.textContent = 'N/A';
	}
}

const CHANGELOG_GROUP_TAGS = {
	Features: 'tag-feat',
	'Bug Fixes': 'tag-fix',
	Documentation: 'tag-docs',
	Refactor: 'tag-refactor',
	Performance: 'tag-feat',
};

function changelogTagClass(group) {
	return CHANGELOG_GROUP_TAGS[group] || 'tag-chore';
}

function escapeHtml(str) {
	const div = document.createElement('div');
	div.textContent = str;
	return div.innerHTML;
}

async function loadChangelog() {
	const container = document.getElementById('changelog-content');
	if (!container) return;

	try {
		const releases = await loadChangelogData();

		const withCommits = (releases || []).filter(r => (r.commits || []).length > 0);
		if (withCommits.length === 0) {
			renderChangelogEmpty(container);
			return;
		}

		const unreleased = withCommits.filter(r => !r.version);
		const latestTagged = withCommits.find(r => r.version);
		const visible = [...unreleased, ...(latestTagged ? [latestTagged] : [])];

		const latestTimestamp = visible[0]?.commits?.[0]?.author?.timestamp;
		const footerUpdated = document.getElementById('footer-updated');
		if (footerUpdated && latestTimestamp) {
			const lang = localStorage.getItem(LANG_STORAGE_KEY) || DEFAULT_LANG;
			const t = translations[lang] || translations[DEFAULT_LANG] || {};
			const label = t['changelog-updated'] || 'Last updated: ';
			const date = new Date(latestTimestamp * 1000).toISOString().slice(0, 10);
			footerUpdated.textContent = `${label}${date}`;
		}

		container.innerHTML = visible.map(release => {
			const version = release.version || 'Unreleased';
			const date = release.timestamp
				? new Date(release.timestamp * 1000).toISOString().slice(0, 10)
				: '';

			const entries = (release.commits || []).map(c => {
				const tagClass = changelogTagClass(c.group);
				const label = c.group || 'Other';
				const sha = (c.id || '').slice(0, 7);
				const url = c.id ? `${CHANGELOG_REPO}/commit/${c.id}` : null;
				return `
          <div class="changelog-entry">
            <span class="tag ${tagClass}">${escapeHtml(label)}</span>
            <span>${escapeHtml(c.message || '')}</span>
            ${url ? `<a href="${url}" target="_blank" rel="noopener">${sha}</a>` : ''}
          </div>`;
			}).join('');

			return `
        <div class="changelog-version">
          <h3>${escapeHtml(version)} ${date ? `<span class="changelog-date">— ${date}</span>` : ''}</h3>
          ${entries}
        </div>`;
		}).join('');
	} catch (e) {
		renderChangelogEmpty(container);
	}
}

function renderChangelogEmpty(container) {
	const lang = localStorage.getItem(LANG_STORAGE_KEY) || DEFAULT_LANG;
	const t = translations[lang] || translations[DEFAULT_LANG] || {};
	const message = t['changelog-empty-msg'] || 'No changelog entries yet — check back after the next release.';
	container.innerHTML = `<p class="changelog-empty">${message}</p>`;
}
